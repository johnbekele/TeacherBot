"""
AI Tool Handlers
Implements the actual execution logic for each AI-callable tool
"""
from typing import Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import re


class AIToolHandlers:
    """Handlers for AI tool execution"""

    def __init__(self, db: AsyncIOMotorDatabase, user_id: str):
        self.db = db
        self.user_id = user_id

    async def handle_display_learning_content(self, input_data: Dict) -> Dict:
        """
        Store and display AI-generated learning content

        Args:
            input_data: {title, content_type, sections}

        Returns:
            {success, content_id}
        """
        content_id = f"content_{str(ObjectId())}"

        content_doc = {
            "content_id": content_id,
            "title": input_data["title"],
            "content_type": input_data["content_type"],
            "sections": input_data["sections"],
            "created_for_user": self.user_id,
            "generated_by_ai": True,
            "created_at": datetime.utcnow()
        }

        await self.db.learning_content.insert_one(content_doc)

        return {
            "success": True,
            "content_id": content_id,
            "message": f"Content '{input_data['title']}' created and ready to display"
        }

    async def handle_generate_exercise(self, input_data: Dict) -> Dict:
        """
        Generate and store a new exercise

        Args:
            input_data: {title, description, prompt, difficulty, exercise_type, starter_code, solution, test_cases, node_id}

        Returns:
            {success, exercise_id}
        """
        exercise_id = f"ai_ex_{str(ObjectId())}"
        node_id = input_data.get("node_id", "dynamic")

        # Validate content was shown first (content gate)
        if node_id != "dynamic":
            # Check if content was displayed
            content_shown = await self.db.learning_content.find_one({
                "created_for_user": self.user_id,
                "title": {"$regex": f".*{node_id}.*", "$options": "i"}
            })

            if not content_shown:
                # Check if pre-generated content exists but wasn't displayed
                pre_gen = await self.db.course_content.find_one({
                    "node_id": node_id,
                    "user_id": self.user_id
                })

                if pre_gen:
                    return {
                        "success": False,
                        "error": "content_not_shown",
                        "message": f"⚠️ You must display the lecture content first using `display_learning_content`. Pre-generated content is available - show it to the user before creating exercises.",
                        "available_sections": len(pre_gen.get('lecture', {}).get('sections', []))
                    }
                else:
                    # No pre-generated content, but still need to create content first
                    return {
                        "success": False,
                        "error": "content_not_shown",
                        "message": f"⚠️ You must display lecture content first using `display_learning_content`. Create and show educational content before exercises."
                    }

        # Fetch user profile for personalization
        user_profile = await self.db.user_profiles.find_one({"user_id": self.user_id})
        if not user_profile:
            user_profile = {"experience_level": "beginner", "learning_style": "mixed"}

        experience_level = user_profile.get("experience_level", "beginner")

        # Auto-adjust difficulty if not specified
        if "difficulty" not in input_data or not input_data["difficulty"]:
            input_data["difficulty"] = {
                "beginner": "beginner",
                "intermediate": "intermediate",
                "advanced": "advanced"
            }.get(experience_level, "beginner")

        # Add scaffolding for beginners
        if experience_level == "beginner" and "starter_code" in input_data:
            starter = input_data["starter_code"]
            if "TODO" not in starter and "# Your code here" not in starter:
                # Add helpful TODO comments for beginners
                input_data["starter_code"] = f"# TODO: Implement the solution\n# Hint: Break it into small steps\n\n{starter}"

        # Prepare test cases
        # Handle both string and list formats
        test_cases_input = input_data.get("test_cases", [])
        if isinstance(test_cases_input, str):
            # Parse JSON string
            import json
            try:
                test_cases_input = json.loads(test_cases_input)
            except json.JSONDecodeError:
                test_cases_input = []

        test_cases = []
        for tc in test_cases_input:
            test_cases.append({
                "test_id": tc["test_id"],
                "description": tc["description"],
                "input": tc.get("input", {}),
                "expected_output": tc.get("expected_output", {"stdout": ""}),
                "validation_script": tc["validation_script"]
            })

        # If no test cases provided, create a basic one using validation_script
        if not test_cases:
            test_cases.append({
                "test_id": "test_1",
                "description": "Basic functionality test",
                "input": {},
                "expected_output": {"stdout": ""},
                "validation_script": "# Test execution"
            })

        exercise_doc = {
            "exercise_id": exercise_id,
            "node_id": input_data.get("node_id", "dynamic"),
            "title": input_data["title"],
            "description": input_data["description"],
            "prompt": input_data["prompt"],
            "type": input_data["exercise_type"],
            "difficulty": input_data["difficulty"],
            "starter_code": input_data.get("starter_code", "# Your code here"),
            "solution": input_data["solution"],
            "test_cases": test_cases,
            "hints": [],
            "grading_rubric": {
                "correctness_weight": 1.0,
                "style_weight": 0.0,
                "efficiency_weight": 0.0
            },
            "generated_by_ai": True,
            "created_for_user": self.user_id,
            "created_at": datetime.utcnow()
        }

        await self.db.exercises.insert_one(exercise_doc)

        return {
            "success": True,
            "exercise_id": exercise_id,
            "message": f"Exercise '{input_data['title']}' created and ready for practice"
        }

    async def handle_navigate_to_next_step(self, input_data: Dict) -> Dict:
        """
        Control learning flow navigation - automatically navigate user to next step

        Args:
            input_data: {target_type, target_id, reason}
            target_type: "exercise", "node", or "content"
            target_id: ID of the exercise, node, or content to navigate to
            reason: Brief explanation of why moving to this step

        Returns:
            {success, action} - action object triggers frontend navigation
        """
        target_type = input_data.get("target_type", "exercise")
        target_id = input_data.get("target_id")
        reason = input_data.get("reason", "")

        print(f"🚀 AI Navigation: {target_type} → {target_id} (Reason: {reason})")

        # Return action in format expected by frontend ChatPanel
        return {
            "success": True,
            "action": {
                "type": f"navigate_to_{target_type}",
                f"{target_type}_id": target_id,
                "reason": reason
            },
            "message": f"Navigating to {target_type}..."
        }

    async def handle_provide_feedback(self, input_data: Dict) -> Dict:
        """
        Provide personalized feedback

        Args:
            input_data: {feedback_type, message, strengths, improvements, next_action}

        Returns:
            {success, feedback}
        """
        feedback = {
            "feedback_type": input_data["feedback_type"],
            "message": input_data["message"],
            "strengths": input_data.get("strengths", []),
            "improvements": input_data.get("improvements", []),
            "next_action": input_data["next_action"],
            "created_at": datetime.utcnow().isoformat()
        }

        return {
            "success": True,
            "feedback": feedback
        }

    async def handle_update_user_progress(self, input_data: Dict) -> Dict:
        """
        Update user's learning progress

        Args:
            input_data: {node_id, status, completion_percentage}

        Returns:
            {success}
        """
        node_id = input_data["node_id"]
        status = input_data["status"]
        completion_percentage = input_data.get("completion_percentage", 0)

        # Update user progress for this node
        await self.db.user_progress.update_one(
            {
                "user_id": self.user_id,
                "node_id": node_id
            },
            {
                "$set": {
                    "status": status,
                    "completion_percentage": completion_percentage,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        return {
            "success": True,
            "message": f"Progress updated: {node_id} - {status} ({completion_percentage}%)"
        }

    async def handle_execute_code(self, input_data: Dict) -> Dict:
        """
        Simulate code execution using AI and return predicted output.

        Instead of actually running code (costly on cloud), AI analyzes
        the code and predicts what the output would be.

        Args:
            input_data: {code, language, explanation}

        Returns:
            {success, output, simulated, component}
        """
        from anthropic import AsyncAnthropic
        from app.config import get_settings

        settings = get_settings()
        code = input_data["code"]
        language = input_data["language"]
        explanation = input_data["explanation"]

        try:
            # Use Claude Haiku for fast, cheap output prediction
            client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

            response = await client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=500,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": f"""Predict the exact output of this {language} code. Return ONLY the output that would appear in the terminal/console, nothing else. If there would be no output, return "(no output)". If there would be an error, return the error message.

```{language}
{code}
```"""
                }]
            )

            predicted_output = response.content[0].text.strip()

            # Return component data for frontend to render
            return {
                "success": True,
                "output": predicted_output,
                "simulated": True,
                "explanation": explanation,
                "component": {
                    "type": "code_execution_simulated",
                    "language": language,
                    "code": code,
                    "output": predicted_output
                }
            }

        except Exception as e:
            print(f"AI simulation error: {str(e)}")
            return {
                "success": False,
                "output": f"Could not simulate output: {str(e)}",
                "simulated": True,
                "component": {"type": "error", "message": str(e)}
            }

    async def handle_show_interactive_component(self, input_data: Dict) -> Dict:
        """
        Prepare interactive component data for frontend rendering

        Args:
            input_data: {component_type, data, message}

        Returns:
            {success, component}
        """
        component_type = input_data["component_type"]
        data = input_data["data"]
        message = input_data["message"]

        # Build component object for frontend
        component = {
            "type": component_type,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }

        return {
            "success": True,
            "component": component,
            "message": f"Interactive {component_type} component ready"
        }

    async def handle_save_user_profile(self, input_data: Dict) -> Dict:
        """
        Save user's learning profile from onboarding

        Args:
            input_data: {experience_level, learning_goals, background, learning_style, adhd_accommodations, available_time, specific_interests}

        Returns:
            {success, message}
        """
        from datetime import datetime

        # Create or update user profile
        profile_doc = {
            "user_id": self.user_id,
            "experience_level": input_data["experience_level"],
            "learning_goals": input_data["learning_goals"],
            "background": input_data.get("background", ""),
            "learning_style": input_data["learning_style"],
            "adhd_accommodations": input_data.get("adhd_accommodations", False),
            "available_time": input_data.get("available_time", ""),
            "specific_interests": input_data.get("specific_interests", []),
            "weak_points": [],
            "strong_areas": [],
            "total_exercises_completed": 0,
            "total_exercises_failed": 0,
            "average_score": 0.0,
            "last_active": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Update or insert profile
        await self.db.user_profiles.update_one(
            {"user_id": self.user_id},
            {"$set": profile_doc},
            upsert=True
        )

        return {
            "success": True,
            "message": f"✅ Learning profile saved! Your personalized learning experience is ready."
        }

    async def handle_create_learning_path(self, input_data: Dict) -> Dict:
        """
        Create a new learning path structure in database

        Args:
            input_data: {
                path_id, title, description, thumbnail, color, category
            }

        Returns:
            {success, path_id, message, created_path}
        """
        path_id = input_data["path_id"]

        # Check if path already exists
        existing = await self.db.learning_paths.find_one({"path_id": path_id, "user_id": self.user_id})
        if existing:
            return {
                "success": False,
                "message": f"Learning path '{path_id}' already exists! You can view it in your learning paths."
            }

        # Create learning path document
        path_doc = {
            "path_id": path_id,
            "title": input_data["title"],
            "description": input_data["description"],
            "thumbnail": input_data.get("thumbnail", "🎯"),
            "color": input_data.get("color", "#6366F1"),
            "category": input_data.get("category", "custom"),
            "user_id": self.user_id,
            "created_by": "ai",
            "created_at": datetime.utcnow(),
            "status": "active",
            "node_prefixes": [path_id]  # Nodes for this path should start with path_id
        }

        # Insert into database
        await self.db.learning_paths.insert_one(path_doc)

        return {
            "success": True,
            "path_id": path_id,
            "message": f"✅ Created learning path '{input_data['title']}'! Now I'll create learning modules for this path. You can view the path in your Learning Paths section.",
            "created_path": {
                "path_id": path_id,
                "title": input_data["title"],
                "description": input_data["description"],
                "thumbnail": path_doc["thumbnail"],
                "color": path_doc["color"]
            }
        }

    async def _validate_planning_prerequisites(self, session_id: str) -> Dict:
        """
        Validate Planning AI asked required questions before creating nodes

        Returns:
            {
                "can_create_nodes": bool,
                "questions_asked": int,
                "missing": List[str]
            }
        """
        # Get recent chat messages for this session
        messages = await self.db.chat_messages.find({
            "session_id": session_id,
            "role": "assistant"
        }).sort("timestamp", -1).limit(10).to_list(length=10)

        # Check for required question patterns
        required_patterns = [
            r"experience.*level|level.*experience",  # Experience level question
            r"used.*before|worked.*with|familiar",   # Prior usage question
            r"similar.*tool|other.*tools"            # Similar tools question
        ]

        questions_asked = sum(
            1 for pattern in required_patterns
            if any(re.search(pattern, msg.get("content", ""), re.IGNORECASE)
                   for msg in messages)
        )

        missing = []
        if questions_asked < 2:
            missing.append("Experience level")
            missing.append("Prior knowledge")

        return {
            "can_create_nodes": questions_asked >= 2,
            "questions_asked": questions_asked,
            "missing": missing
        }

    async def handle_create_learning_node(self, input_data: Dict) -> Dict:
        """
        Create a new learning node in database and add to user's learning path

        Args:
            input_data: {
                node_id, title, description, difficulty,
                estimated_duration, prerequisites, concepts, learning_objectives
            }

        Returns:
            {success, node_id, message, created_node}
        """
        node_id = input_data["node_id"]

        # Validate planning prerequisites (must ask 2+ questions first)
        if hasattr(self, 'current_session_id') and self.current_session_id:
            validation = await self._validate_planning_prerequisites(self.current_session_id)

            if not validation["can_create_nodes"]:
                return {
                    "success": False,
                    "error": "prerequisite_not_met",
                    "message": f"⚠️ Please ask the user about: {', '.join(validation['missing'])}. You've only asked {validation['questions_asked']}/2 required questions.",
                    "required_questions": ["Experience level with this topic", "Prior knowledge or similar tools used"]
                }

        # Check if node already exists
        existing = await self.db.learning_nodes.find_one({"node_id": node_id})
        if existing:
            return {
                "success": False,
                "message": f"Node '{node_id}' already exists. You can start learning from it now!"
            }

        # Create comprehensive node document
        node_doc = {
            "node_id": node_id,
            "title": input_data["title"],
            "description": input_data["description"],
            "difficulty": input_data["difficulty"],
            "estimated_duration": input_data.get("estimated_duration", 30),
            "prerequisites": input_data.get("prerequisites", []),
            "skills_taught": input_data.get("concepts", []),
            "content": {
                "introduction": input_data["description"],
                "concepts": input_data["concepts"],
                "learning_objectives": input_data["learning_objectives"],
                "practical_applications": [],
                "sections": []
            },
            "exercises": [],
            "created_by": "ai",
            "created_for_user": self.user_id,
            "created_at": datetime.utcnow(),
            "tags": [input_data["difficulty"], "ai-generated"],
            "status": "active"
        }

        # Insert into database
        result = await self.db.learning_nodes.insert_one(node_doc)

        # Add to user's learning path
        await self.db.user_progress.update_one(
            {"user_id": self.user_id, "node_id": node_id},
            {
                "$set": {
                    "status": "not_started",
                    "completion_percentage": 0,
                    "started_at": None,
                    "completed_at": None,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        # Trigger bulk content generation if enough nodes created
        # Extract path_id from node_id (e.g., "python-variables" -> "python")
        path_id = node_id.split("-")[0] if "-" in node_id else node_id

        # Count nodes in this path
        nodes_in_path_count = await self.db.learning_nodes.count_documents({
            "node_id": {"$regex": f"^{path_id}"}
        })

        # If we've reached 3+ nodes, trigger bulk generation
        if nodes_in_path_count >= 3:
            # Check if content already generated for this path/user
            existing_content = await self.db.course_content.count_documents({
                "path_id": path_id,
                "user_id": self.user_id
            })

            # Only generate if not already generated
            if existing_content == 0:
                import asyncio
                from app.ai.content_generator import generate_full_course_content

                # Get user profile for personalization
                user_profile = await self.db.user_profiles.find_one({"user_id": self.user_id}) or {}

                # Get path info if it exists
                path_doc = await self.db.learning_paths.find_one({"path_id": path_id, "user_id": self.user_id})
                path_description = path_doc.get("description", "") if path_doc else f"Learn {path_id}"

                print(f"🚀 Triggering bulk content generation for path: {path_id} ({nodes_in_path_count} nodes)")

                # Trigger async generation (don't block)
                asyncio.create_task(
                    generate_full_course_content(
                        db=self.db,
                        user_id=self.user_id,
                        path_id=path_id,
                        path_description=path_description,
                        target_nodes=[],  # Will fetch from DB
                        user_profile=user_profile
                    )
                )

        return {
            "success": True,
            "node_id": node_id,
            "message": f"✅ Created learning node '{input_data['title']}'! It's now available in your learning path. You can click on it to start learning." + (f" 📚 Generating personalized course content in background..." if nodes_in_path_count >= 3 else ""),
            "created_node": {
                "node_id": node_id,
                "title": input_data["title"],
                "difficulty": input_data["difficulty"],
                "estimated_duration": input_data.get("estimated_duration", 30)
            }
        }
