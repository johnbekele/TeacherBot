"""
Tool Registry for AI Tool Calling
Centralizes tool definitions and execution routing
"""
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
import json

from app.ai.tool_handlers import AIToolHandlers
from app.ai.behavioral_tools import BehavioralTools, get_tool_definitions as get_behavioral_tool_defs


class ToolRegistry:
    """Registry for AI-callable tools with Claude API definitions"""

    def __init__(self, db: AsyncIOMotorDatabase, user_id: str):
        self.db = db
        self.user_id = user_id
        self.handlers = AIToolHandlers(db, user_id)
        self.behavioral_tools = BehavioralTools(db, user_id)
        self.tools = {}
        self._register_tools()

    def _register_tools(self):
        """Register all available tools with their Claude API definitions"""

        # Tool 1: Display Learning Content
        self.tools["display_learning_content"] = {
            "name": "display_learning_content",
            "description": "Display educational content (notes, explanations, concept breakdowns) to the user. Use this to teach concepts before exercises or provide custom notes.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the content"
                    },
                    "content_type": {
                        "type": "string",
                        "enum": ["note", "explanation", "example", "summary", "reference"],
                        "description": "Type of educational content"
                    },
                    "sections": {
                        "type": "array",
                        "description": "Content broken into sections",
                        "items": {
                            "type": "object",
                            "properties": {
                                "heading": {
                                    "type": "string",
                                    "description": "Section heading"
                                },
                                "body": {
                                    "type": "string",
                                    "description": "Main content in Markdown format"
                                },
                                "code_example": {
                                    "type": "string",
                                    "description": "Optional code snippet"
                                },
                                "language": {
                                    "type": "string",
                                    "description": "Programming language of code example"
                                }
                            },
                            "required": ["heading", "body"]
                        }
                    }
                },
                "required": ["title", "content_type", "sections"]
            }
        }

        # Tool 2: Generate Exercise
        self.tools["generate_exercise"] = {
            "name": "generate_exercise",
            "description": "Generate a coding exercise dynamically based on the topic and user's skill level. Creates a new practice problem with test cases.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short, descriptive title for the exercise"
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of what this exercise teaches"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Detailed instructions for the student"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                        "description": "Difficulty level"
                    },
                    "exercise_type": {
                        "type": "string",
                        "enum": ["python", "bash", "terraform", "pulumi", "ansible"],
                        "description": "Programming language or tool"
                    },
                    "starter_code": {
                        "type": "string",
                        "description": "Initial code template"
                    },
                    "solution": {
                        "type": "string",
                        "description": "Complete solution code"
                    },
                    "test_cases": {
                        "type": "array",
                        "description": "Test cases to validate solution",
                        "items": {
                            "type": "object",
                            "properties": {
                                "test_id": {"type": "string"},
                                "description": {"type": "string"},
                                "validation_script": {"type": "string"}
                            },
                            "required": ["test_id", "description", "validation_script"]
                        }
                    },
                    "node_id": {
                        "type": "string",
                        "description": "Associated learning node"
                    }
                },
                "required": ["title", "description", "prompt", "difficulty", "exercise_type", "solution"]
            }
        }

        # Tool 3: Navigate to Next Step
        self.tools["navigate_to_next_step"] = {
            "name": "navigate_to_next_step",
            "description": "Navigate the user to the next learning step (exercise or content node). Use this to automatically move them forward after completing current activity.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "target_type": {
                        "type": "string",
                        "enum": ["exercise", "node"],
                        "description": "Type of target to navigate to: 'exercise' for practice exercises, 'node' for learning content"
                    },
                    "target_id": {
                        "type": "string",
                        "description": "ID of the exercise or node to navigate to"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief explanation of why moving to this step (helps user understand progression)"
                    }
                },
                "required": ["target_type", "target_id"]
            }
        }

        # Tool 4: Provide Feedback
        self.tools["provide_feedback"] = {
            "name": "provide_feedback",
            "description": "Provide personalized feedback on user's exercise submission. Use after evaluating their code to guide improvement.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "feedback_type": {
                        "type": "string",
                        "enum": ["success", "partial_success", "needs_improvement", "excellent"],
                        "description": "Overall assessment"
                    },
                    "message": {
                        "type": "string",
                        "description": "Main feedback message"
                    },
                    "strengths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "What the student did well"
                    },
                    "improvements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Areas to improve"
                    },
                    "next_action": {
                        "type": "string",
                        "description": "What student should do next"
                    }
                },
                "required": ["feedback_type", "message", "next_action"]
            }
        }

        # Tool 5: Update User Progress
        self.tools["update_user_progress"] = {
            "name": "update_user_progress",
            "description": "Update the user's learning progress. Use when user completes exercises or milestones.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "Learning node ID"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["not_started", "in_progress", "completed"],
                        "description": "Current status"
                    },
                    "completion_percentage": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100,
                        "description": "Percentage completed"
                    }
                },
                "required": ["node_id", "status"]
            }
        }

        # Tool 6: Execute Code (NEW!)
        self.tools["execute_code"] = {
            "name": "execute_code",
            "description": "Execute code snippets and show output to the user in chat. Use this to demonstrate concepts, debug code, or show examples. Perfect for 'let me show you' moments!",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to execute"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "javascript", "bash"],
                        "description": "Programming language"
                    },
                    "explanation": {
                        "type": "string",
                        "description": "Brief explanation of what this code does (shown to user)"
                    }
                },
                "required": ["code", "language", "explanation"]
            }
        }

        # Tool 7: Show Interactive Component (NEW!)
        self.tools["show_interactive_component"] = {
            "name": "show_interactive_component",
            "description": "Render interactive UI components in the chat. Use for quizzes, buttons, code editors, or visual demonstrations.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "component_type": {
                        "type": "string",
                        "enum": ["quiz", "code_editor", "button", "info_box", "progress_bar"],
                        "description": "Type of component to render"
                    },
                    "data": {
                        "type": "object",
                        "description": "Component-specific data (e.g., quiz questions, button label, code content)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message to show with the component"
                    }
                },
                "required": ["component_type", "data", "message"]
            }
        }

        # Tool 8: Save User Profile (For Onboarding!)
        self.tools["save_user_profile"] = {
            "name": "save_user_profile",
            "description": "Save user's learning profile from onboarding. Use after gathering user information through questions.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "experience_level": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                        "description": "User's experience level"
                    },
                    "learning_goals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "What they want to learn"
                    },
                    "background": {
                        "type": "string",
                        "description": "Previous experience (e.g., 'Python developer, knows CLI')"
                    },
                    "learning_style": {
                        "type": "string",
                        "enum": ["hands_on", "read_first", "mixed"],
                        "description": "Preferred learning style"
                    },
                    "adhd_accommodations": {
                        "type": "boolean",
                        "description": "Whether user needs ADHD accommodations"
                    },
                    "available_time": {
                        "type": "string",
                        "description": "Hours per week (e.g., '5-7 hours')"
                    },
                    "specific_interests": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific tools/topics mentioned"
                    }
                },
                "required": ["experience_level", "learning_goals", "learning_style"]
            }
        }

        # Tool 9: Create Learning Node (For Planning AI!)
        self.tools["create_learning_node"] = {
            "name": "create_learning_node",
            "description": "Create a new learning topic/node in the user's learning path. Use this AFTER analyzing what the user wants to learn. Creates actual clickable nodes that appear in the Learning Path.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "Unique ID for the node (use lowercase with hyphens, e.g., 'docker-basics')"
                    },
                    "title": {
                        "type": "string",
                        "description": "Display title (e.g., 'Docker Basics')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of what this node teaches"
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                        "description": "Difficulty level"
                    },
                    "estimated_duration": {
                        "type": "integer",
                        "description": "Estimated time in minutes"
                    },
                    "prerequisites": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of prerequisite node IDs"
                    },
                    "concepts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Key concepts covered (bulleted list)"
                    },
                    "learning_objectives": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "What user will learn"
                    }
                },
                "required": ["node_id", "title", "description", "difficulty", "concepts", "learning_objectives"]
            }
        }

        # BEHAVIORAL TRACKING TOOLS (Tools 10-12) - NEW for Week 2!
        # These allow AI to observe and record user behavior patterns for personalization

        behavioral_tool_defs = get_behavioral_tool_defs()
        for tool_def in behavioral_tool_defs:
            self.tools[tool_def["name"]] = tool_def

    async def execute_tool(self, tool_name: str, tool_input: Dict) -> str:
        """
        Execute a tool by name and return JSON result

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            JSON string with tool execution result
        """
        if tool_name not in self.tools:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        try:
            # Check if this is a behavioral tracking tool
            behavioral_tool_names = ["record_struggle_indicator", "record_engagement_metric", "analyze_error_pattern"]

            if tool_name in behavioral_tool_names:
                # Route to behavioral tools handler
                handler = getattr(self.behavioral_tools, tool_name, None)

                if not handler:
                    return json.dumps({"error": f"No behavioral handler for tool: {tool_name}"})

                result = await handler(**tool_input)
                return result  # Already returns string, don't double-encode

            else:
                # Route to regular tool handler
                handler = getattr(self.handlers, f"handle_{tool_name}", None)

                if not handler:
                    return json.dumps({"error": f"No handler for tool: {tool_name}"})

                result = await handler(tool_input)
                return json.dumps(result)

        except Exception as e:
            return json.dumps({
                "error": f"Tool execution failed: {str(e)}",
                "tool_name": tool_name
            })

    def get_tool_definitions(self) -> List[Dict]:
        """
        Get all tool definitions in Claude API format

        Returns:
            List of tool definition dictionaries
        """
        return list(self.tools.values())
