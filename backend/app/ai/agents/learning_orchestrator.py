"""
Learning Orchestrator Agent
Main AI agent that controls the entire learning experience through tool calling
"""
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.ai.chat_service import ChatService
from app.ai.tool_registry import ToolRegistry
from app.ai.prompts.system_prompts import get_system_prompt, EXERCISE_FEEDBACK_PROMPT
from app.api.v1.user_context import get_user_context_for_ai


class LearningOrchestrator:
    """AI agent that orchestrates the dynamic learning experience"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.chat_service = ChatService(db)

    async def start_learning_session(
        self,
        user_id: str,
        node_id: str
    ) -> Dict:
        """
        Initialize AI-driven learning session for a node

        Args:
            user_id: User ID
            node_id: Learning node ID

        Returns:
            Dict with session_id, message, content_id/exercise_id, actions
        """
        # Get node information
        node = await self.db.learning_nodes.find_one({"node_id": node_id})
        if not node:
            return {
                "error": "Node not found",
                "message": "The requested learning module was not found."
            }

        # Get user context for personalization
        user_context = await get_user_context_for_ai(self.db, user_id)

        # Get user's progress on this node
        progress = await self.db.user_progress.find_one({
            "user_id": user_id,
            "node_id": node_id
        })

        # Create or get learning session
        session_id = await self.chat_service.get_or_create_session(
            user_id=user_id,
            context_type="learning_session",
            context_id=node_id
        )

        # Initialize tool registry for this user
        tool_registry = ToolRegistry(self.db, user_id)

        # Build orchestrator system prompt
        system_prompt = self._build_orchestrator_prompt(node, user_context, progress)

        # Initial message to AI
        if progress and progress.get("status") == "in_progress":
            initial_message = f"User is continuing their learning of: {node['title']}. Welcome them back and continue from where they left off."
        else:
            initial_message = f"User just clicked 'Start Learning' for: {node['title']}. Begin teaching this topic."

        print(f"🎓 Starting learning session for node: {node['title']}")

        # Send message with tools enabled
        response = await self.chat_service.send_message(
            user_id=user_id,
            session_id=session_id,
            message=initial_message,
            system_prompt=system_prompt,
            context_data={"node": node},
            tools=tool_registry.get_tool_definitions(),
            tool_executor=tool_registry.execute_tool
        )

        return response

    async def handle_exercise_submission(
        self,
        user_id: str,
        exercise_id: str,
        code: str,
        test_results: Dict
    ) -> Dict:
        """
        AI analyzes exercise submission and decides next step

        Args:
            user_id: User ID
            exercise_id: Exercise ID
            code: Submitted code
            test_results: {score, passed, test_results}

        Returns:
            Dict with AI response and next action
        """
        # Get exercise details
        exercise = await self.db.exercises.find_one({"exercise_id": exercise_id})
        if not exercise:
            return {
                "error": "Exercise not found",
                "message": "Could not find the exercise."
            }

        # Get or create session for this exercise
        session_id = await self.chat_service.get_or_create_session(
            user_id=user_id,
            context_type="exercise",
            context_id=exercise_id
        )

        # Initialize tool registry
        tool_registry = ToolRegistry(self.db, user_id)

        # Build context for AI
        context_data = {
            "exercise": exercise,
            "user_code": code,
            "test_results": test_results
        }

        # Build prompt for post-submission analysis
        system_prompt = await self._build_post_submission_prompt(user_id)

        # Message to AI
        status = "PASSED" if test_results["passed"] else "FAILED"
        message = f"""User submitted code for exercise: {exercise['title']}

Results: {test_results['score']}% - {status}

Test Results: {test_results.get('test_results', [])}

Analyze their submission:
1. Use `provide_feedback` to give specific, actionable feedback
2. Use `navigate_to_next_step` to automatically move them forward if they passed, or suggest retry if they didn't"""

        print(f"📝 Exercise submission: {exercise['title']} - Score: {test_results['score']}%")

        # AI analyzes and responds with tools
        response = await self.chat_service.send_message(
            user_id=user_id,
            session_id=session_id,
            message=message,
            system_prompt=system_prompt,
            context_data=context_data,
            tools=tool_registry.get_tool_definitions(),
            tool_executor=tool_registry.execute_tool
        )

        return response

    async def continue_learning(
        self,
        user_id: str,
        session_id: str,
        message: str
    ) -> Dict:
        """
        Continue ongoing learning conversation

        Args:
            user_id: User ID
            session_id: Session ID
            message: User's message

        Returns:
            AI response with possible tool invocations
        """
        # Initialize tool registry
        tool_registry = ToolRegistry(self.db, user_id)

        # Get session to understand context
        session = await self.db.chat_sessions.find_one({"_id": ObjectId(session_id)})
        if not session:
            return {"error": "Session not found"}

        # Build appropriate system prompt based on context
        system_prompt = get_system_prompt("learning_orchestrator")

        # Send message with tools
        response = await self.chat_service.send_message(
            user_id=user_id,
            session_id=session_id,
            message=message,
            system_prompt=system_prompt,
            tools=tool_registry.get_tool_definitions(),
            tool_executor=tool_registry.execute_tool
        )

        return response

    def _build_orchestrator_prompt(
        self,
        node: Dict,
        user_context: str,
        progress: Optional[Dict]
    ) -> str:
        """Build system prompt for learning orchestrator"""

        base_prompt = get_system_prompt("learning_orchestrator")

        node_info = f"""
CURRENT LEARNING MODULE:
Title: {node['title']}
Description: {node['description']}
Difficulty: {node['difficulty']}
Skills to teach: {', '.join(node.get('skills_taught', []))}"""

        progress_info = ""
        if progress:
            progress_info = f"""
CURRENT PROGRESS:
Status: {progress.get('status', 'not_started')}
Completion: {progress.get('completion_percentage', 0)}%"""

        enhanced_prompt = f"""{base_prompt}

{node_info}

{progress_info}

USER CONTEXT:
{user_context}

Remember: Use your tools to make things happen! Don't just talk about teaching - use `display_learning_content` to actually create content, `generate_exercise` to create practice problems, and `navigate_to_next_step` to move them forward."""

        return enhanced_prompt

    async def _build_post_submission_prompt(self, user_id: str) -> str:
        """Build prompt for post-exercise submission analysis"""

        user_context = await get_user_context_for_ai(self.db, user_id)

        # Get user profile with weak points
        profile = await self.db.user_profiles.find_one({"user_id": user_id})
        weak_points_info = ""
        if profile and profile.get("weak_points"):
            weak_topics = [wp.get("topic", "") for wp in profile["weak_points"][-5:]]  # Last 5 weak points
            if weak_topics:
                weak_points_info = f"\n\nUSER'S WEAK POINTS (target these in exercises):\n- " + "\n- ".join(weak_topics)

        return f"""{get_system_prompt("learning_orchestrator")}

USER CONTEXT:
{user_context}
{weak_points_info}

CURRENT TASK: Analyze exercise submission and provide feedback

{EXERCISE_FEEDBACK_PROMPT}

Use your tools:
1. `provide_feedback` - Give specific, constructive feedback
2. `navigate_to_next_step` - Automatically guide them to next activity
3. `generate_exercise` - Create follow-up exercise that targets their weak points

CRITICAL: When creating next exercise, include practice for their weak areas!
For example, if they struggle with loops → create exercise requiring loop iteration
If they struggle with functions → create exercise requiring function definitions

If they passed: Celebrate success and create next challenge (slightly harder, targets weak points)
If they failed: Provide encouragement and create simpler exercise focusing on same concepts"""
