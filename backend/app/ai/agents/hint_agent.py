"""
Hint Generator Agent for progressive exercise hints
"""
from typing import Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.ai.chat_service import ChatService
from app.ai.prompts.system_prompts import get_system_prompt
from app.api.v1.user_context import get_user_context_for_ai


class HintAgent:
    """Generates progressive hints for exercises"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.chat_service = ChatService(db)

    async def _get_enhanced_system_prompt(self, user_id: str) -> str:
        """Get system prompt enhanced with user context"""
        base_prompt = get_system_prompt("hint")
        user_context = await get_user_context_for_ai(self.db, user_id)

        enhanced_prompt = f"""{base_prompt}

USER CONTEXT:
{user_context}

Tailor your hints to match the user's experience level and learning style. If they have specific learning challenges, adjust your language and pacing accordingly."""

        return enhanced_prompt

    async def generate_hint(
        self,
        user_id: str,
        exercise_id: str,
        hint_level: int,
        user_code: str = "",
        previous_attempts: int = 0,
    ) -> Dict:
        """
        Generate a hint for the current exercise

        Args:
            user_id: Student's user ID
            exercise_id: Current exercise ID
            hint_level: Which hint number (1-4)
            user_code: Student's current code
            previous_attempts: Number of failed attempts
        """
        # Get exercise details (exercises use exercise_id string, not _id ObjectId)
        exercise = await self.db.exercises.find_one({"exercise_id": exercise_id})
        if not exercise:
            raise ValueError("Exercise not found")

        # Build hint request based on level
        hint_request = self._build_hint_request(
            exercise, hint_level, user_code, previous_attempts
        )

        # Get or create session
        session_id = await self.chat_service.get_or_create_session(
            user_id=user_id, context_type="hints", context_id=exercise_id
        )

        # Build context
        context_data = {
            "exercise": {
                "title": exercise.get("title"),
                "description": exercise.get("description"),
                "difficulty": exercise.get("difficulty"),
            },
            "user_code": user_code,
            "hint_level": hint_level,
            "previous_attempts": previous_attempts,
        }

        # Get hint from AI with enhanced prompt
        system_prompt = await self._get_enhanced_system_prompt(user_id)
        response = await self.chat_service.send_message(
            user_id=user_id,
            session_id=session_id,
            message=hint_request,
            system_prompt=system_prompt,
            context_data=context_data,
        )

        # Track hint usage
        await self._track_hint_usage(user_id, exercise_id, hint_level)

        return {
            "hint": response["message"],
            "hint_level": hint_level,
            "exercise_id": exercise_id,
        }

    def _build_hint_request(
        self,
        exercise: Dict,
        hint_level: int,
        user_code: str,
        previous_attempts: int,
    ) -> str:
        """Build the hint request message based on level"""
        base = f"I need help with the exercise: {exercise.get('title', 'N/A')}\n"

        if hint_level == 1:
            return base + "Can you give me a hint to get started?"

        elif hint_level == 2:
            hint_msg = base + "I've tried but I'm still stuck. Can you give me another hint?"
            if user_code:
                hint_msg += f"\n\nHere's what I have so far:\n```\n{user_code}\n```"
            return hint_msg

        elif hint_level == 3:
            hint_msg = base + "I need more guidance. Can you suggest an approach or structure?"
            if user_code:
                hint_msg += f"\n\nMy current code:\n```\n{user_code}\n```"
            return hint_msg

        else:  # Level 4+
            hint_msg = (
                base
                + "I've tried multiple times but I'm really stuck. Can you give me a more detailed hint?"
            )
            if user_code:
                hint_msg += f"\n\nWhat I have:\n```\n{user_code}\n```"
            if previous_attempts > 0:
                hint_msg += f"\n\nI've attempted this {previous_attempts} times."
            return hint_msg

    async def _track_hint_usage(
        self, user_id: str, exercise_id: str, hint_level: int
    ):
        """Track that user requested a hint"""
        await self.db.hint_tracking.insert_one(
            {
                "user_id": user_id,
                "exercise_id": exercise_id,
                "hint_level": hint_level,
                "requested_at": datetime.utcnow(),
            }
        )

    async def get_hint_history(self, user_id: str, exercise_id: str) -> List[Dict]:
        """Get all hints user has requested for an exercise"""
        hints = (
            await self.db.hint_tracking.find(
                {"user_id": user_id, "exercise_id": exercise_id}
            )
            .sort("requested_at", 1)
            .to_list(length=10)
        )
        return hints
