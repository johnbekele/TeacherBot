"""
AI Tool Handlers
Implements the actual execution logic for each AI-callable tool
"""
from typing import Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime


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
            target_type: "exercise" or "node"
            target_id: ID of the exercise or node to navigate to
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
        Execute code and return output for display in chat

        Args:
            input_data: {code, language, explanation}

        Returns:
            {success, output, execution_time, component}
        """
        import subprocess
        import time

        code = input_data["code"]
        language = input_data["language"]
        explanation = input_data["explanation"]

        try:
            start_time = time.time()

            if language == "python":
                # Execute Python code
                result = subprocess.run(
                    ["python3", "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = result.stdout if result.returncode == 0 else result.stderr

            elif language == "javascript":
                # Execute JavaScript with Node
                result = subprocess.run(
                    ["node", "-e", code],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = result.stdout if result.returncode == 0 else result.stderr

            elif language == "bash":
                # Execute Bash command
                result = subprocess.run(
                    ["bash", "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = result.stdout if result.returncode == 0 else result.stderr
            else:
                output = f"Unsupported language: {language}"

            execution_time = time.time() - start_time

            # Return component data for frontend to render
            return {
                "success": True,
                "output": output.strip(),
                "execution_time": round(execution_time, 3),
                "explanation": explanation,
                "component": {
                    "type": "code_execution",
                    "language": language,
                    "code": code,
                    "output": output.strip()
                }
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "Code execution timed out (5 second limit)",
                "component": {"type": "error", "message": "Execution timeout"}
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Execution error: {str(e)}",
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

        return {
            "success": True,
            "node_id": node_id,
            "message": f"✅ Created learning node '{input_data['title']}'! It's now available in your learning path. You can click on it to start learning.",
            "created_node": {
                "node_id": node_id,
                "title": input_data["title"],
                "difficulty": input_data["difficulty"],
                "estimated_duration": input_data.get("estimated_duration", 30)
            }
        }
