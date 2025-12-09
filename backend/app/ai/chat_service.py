"""
Chat service for managing AI conversations with Claude
"""
from typing import List, Dict, Optional, Callable
from anthropic import AsyncAnthropic
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings

settings = get_settings()


class ChatService:
    """Service for handling AI chat interactions"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-haiku-20240307"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
        reraise=True
    )
    async def _execute_tool_with_retry(
        self, tool_executor: Callable, tool_name: str, tool_input: dict
    ) -> str:
        """
        Execute tool with automatic retry logic.
        Retries up to 3 times with exponential backoff.
        """
        try:
            result = await tool_executor(tool_name, tool_input)
            return result
        except Exception as e:
            print(f"   ⚠️ Tool execution attempt failed: {str(e)}")
            raise  # Let tenacity retry

    async def get_or_create_session(
        self, user_id: str, context_type: str, context_id: Optional[str] = None
    ) -> str:
        """Get existing session or create new one"""
        # Try to find active session
        query = {
            "user_id": user_id,
            "context_type": context_type,
            "is_active": True,
        }
        if context_id:
            query["context_id"] = context_id

        session = await self.db.chat_sessions.find_one(query)

        if session:
            return str(session["_id"])

        # Create new session
        new_session = {
            "user_id": user_id,
            "context_type": context_type,
            "context_id": context_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await self.db.chat_sessions.insert_one(new_session)
        return str(result.inserted_id)

    async def get_session_history(
        self, session_id: str, limit: int = 50
    ) -> List[Dict]:
        """Get chat history for a session"""
        messages = (
            await self.db.chat_messages.find({"session_id": session_id})
            .sort("created_at", -1)
            .limit(limit)
            .to_list(length=limit)
        )
        # Reverse to get chronological order
        return list(reversed(messages))

    async def send_message(
        self,
        user_id: str,
        session_id: str,
        message: str,
        system_prompt: str,
        context_data: Optional[Dict] = None,
        tools: Optional[List[Dict]] = None,
        tool_executor: Optional[Callable] = None,
    ) -> Dict:
        """
        Send message and get AI response with optional tool calling support

        Args:
            user_id: User ID
            session_id: Chat session ID
            message: User message
            system_prompt: System prompt for Claude
            context_data: Additional context data
            tools: List of tool definitions for Claude to use
            tool_executor: Async function to execute tools: async (tool_name, tool_input) -> str

        Returns:
            Dict with message, session_id, timestamp, and any tool-generated IDs
        """
        # Save user message
        user_msg = {
            "session_id": session_id,
            "role": "user",
            "content": message,
            "created_at": datetime.utcnow(),
        }
        await self.db.chat_messages.insert_one(user_msg)

        # Get conversation history
        history = await self.get_session_history(session_id, limit=20)

        # Build messages for Claude
        messages = []
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Add context to system prompt if provided
        enhanced_system = system_prompt
        if context_data:
            context_str = self._format_context(context_data)
            enhanced_system = f"{system_prompt}\n\n{context_str}"

        # Track tool results for return
        tool_results = {
            "content_id": None,
            "exercise_id": None,
            "actions": [],
        }

        # Tool calling loop
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        assistant_content = ""  # Initialize to avoid UnboundLocalError

        while iteration < max_iterations:
            iteration += 1

            # Call Claude API
            api_params = {
                "model": self.model,
                "max_tokens": 4096,
                "system": enhanced_system,
                "messages": messages,
            }

            # Add tools if provided
            if tools:
                api_params["tools"] = tools

            response = await self.client.messages.create(**api_params)

            # Handle different stop reasons
            if response.stop_reason == "end_turn":
                # Normal completion - extract final text
                assistant_content = self._extract_text_content(response.content)
                break

            elif response.stop_reason == "tool_use" and tool_executor:
                # Claude wants to use tools
                # Add assistant's response (including tool calls) to conversation
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Execute tools and collect results
                tool_use_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        # Execute the tool
                        tool_name = block.name
                        tool_input = block.input

                        print(f"🔧 AI invoking tool: {tool_name}")
                        print(f"   Input: {json.dumps(tool_input, indent=2)}")

                        try:
                            # Use retry wrapper for automatic retry with exponential backoff
                            result = await self._execute_tool_with_retry(
                                tool_executor, tool_name, tool_input
                            )
                            result_dict = json.loads(result) if isinstance(result, str) else result

                            # Track important IDs from tool execution
                            if "content_id" in result_dict:
                                tool_results["content_id"] = result_dict["content_id"]
                            if "exercise_id" in result_dict:
                                tool_results["exercise_id"] = result_dict["exercise_id"]
                            if "navigation" in result_dict:
                                tool_results["actions"].append({
                                    "type": "navigate",
                                    "data": result_dict["navigation"]
                                })

                            print(f"   ✅ Tool result: {result}")

                            tool_use_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result
                            })
                        except Exception as e:
                            # Surface detailed error to AI so it can respond appropriately
                            error_detail = {
                                "error": str(e),
                                "tool_name": tool_name,
                                "suggestion": "Tool failed after 3 retry attempts. Please try alternative approach or inform user.",
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            print(f"   ❌ Tool execution error (after retries): {error_detail}")

                            tool_use_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(error_detail),
                                "is_error": True
                            })

                # Add tool results to conversation
                messages.append({
                    "role": "user",
                    "content": tool_use_results
                })

                # Continue loop to get Claude's next response
                continue

            elif response.stop_reason == "max_tokens":
                # Hit token limit
                assistant_content = self._extract_text_content(response.content)
                assistant_content += "\n\n[Response truncated due to length]"
                break
            else:
                # Unexpected stop reason
                assistant_content = self._extract_text_content(response.content)
                break

        # If max iterations reached without setting content
        if iteration >= max_iterations and not assistant_content:
            assistant_content = "I've completed the setup for your learning session. Let's begin!"

        # Save assistant response
        assistant_msg = {
            "session_id": session_id,
            "role": "assistant",
            "content": assistant_content,
            "created_at": datetime.utcnow(),
        }
        await self.db.chat_messages.insert_one(assistant_msg)

        # Update session timestamp
        await self.db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)}, {"$set": {"updated_at": datetime.utcnow()}}
        )

        return {
            "message": assistant_content,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            **tool_results  # Include content_id, exercise_id, actions
        }

    def _extract_text_content(self, content_blocks) -> str:
        """Extract text content from Claude response blocks"""
        text_parts = []
        for block in content_blocks:
            if hasattr(block, 'text'):
                text_parts.append(block.text)
            elif isinstance(block, dict) and 'text' in block:
                text_parts.append(block['text'])
        return "\n".join(text_parts) if text_parts else ""

    def _format_context(self, context_data: Dict) -> str:
        """Format context data for system prompt"""
        context_parts = ["CURRENT CONTEXT:"]

        if "exercise" in context_data:
            ex = context_data["exercise"]
            context_parts.append(f"Exercise: {ex.get('title', 'N/A')}")
            context_parts.append(f"Description: {ex.get('description', 'N/A')}")
            if "difficulty" in ex:
                context_parts.append(f"Difficulty: {ex['difficulty']}")

        if "node" in context_data:
            node = context_data["node"]
            context_parts.append(f"Topic: {node.get('title', 'N/A')}")

        if "user_code" in context_data:
            context_parts.append(f"\nUser's current code:\n```\n{context_data['user_code']}\n```")

        if "test_results" in context_data:
            results = context_data["test_results"]
            context_parts.append(f"\nTest Results: {results.get('passed', 0)}/{results.get('total', 0)} passed")

        if "progress" in context_data:
            prog = context_data["progress"]
            context_parts.append(f"User Progress: {prog.get('nodes_completed', 0)} nodes completed")

        return "\n".join(context_parts)

    async def close_session(self, session_id: str):
        """Mark session as inactive"""
        await self.db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)}, {"$set": {"is_active": False}}
        )
