"""
Behavioral Tracking Tools for AI to observe and record user patterns.
These tools allow the Learning Orchestrator to track struggle indicators,
engagement metrics, and error patterns for adaptive personalization.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Dict, Optional
from anthropic import AsyncAnthropic
from app.config import get_settings
import json

settings = get_settings()


class BehavioralTools:
    """Tools for AI to track user behavior and learning patterns"""

    def __init__(self, db: AsyncIOMotorDatabase, user_id: str):
        self.db = db
        self.user_id = user_id
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def record_struggle_indicator(
        self,
        indicator_type: str,
        context: str,
        severity: str = "medium"
    ) -> str:
        """
        Record when the AI detects a user is struggling.

        Args:
            indicator_type: Type of struggle (e.g., "repeated_hints", "long_pause",
                          "repeated_errors", "confusion_signal", "stuck_on_concept")
            context: Description of what the user is struggling with
            severity: "low", "medium", or "high"

        Returns:
            Confirmation message
        """
        try:
            # Validate severity
            if severity not in ["low", "medium", "high"]:
                severity = "medium"

            # Store struggle indicator
            struggle_event = {
                "user_id": self.user_id,
                "event_type": "struggle_indicator",
                "indicator_type": indicator_type,
                "context": context,
                "severity": severity,
                "timestamp": datetime.utcnow()
            }

            await self.db.behavioral_events.insert_one(struggle_event)

            # Update user profile with struggle summary
            await self.db.user_profiles.update_one(
                {"user_id": self.user_id},
                {
                    "$push": {
                        "recent_struggles": {
                            "$each": [{
                                "type": indicator_type,
                                "context": context,
                                "severity": severity,
                                "timestamp": datetime.utcnow()
                            }],
                            "$slice": -10  # Keep only last 10 struggles
                        }
                    },
                    "$set": {"last_active": datetime.utcnow()}
                },
                upsert=True
            )

            print(f"📊 Recorded struggle indicator: {indicator_type} ({severity}) - {context[:50]}...")

            return f"Successfully recorded struggle indicator: {indicator_type}. This will help personalize future content."

        except Exception as e:
            print(f"❌ Error recording struggle indicator: {str(e)}")
            return f"Error recording struggle indicator: {str(e)}"

    async def record_engagement_metric(
        self,
        metric_type: str,
        value: float,
        context: Optional[str] = None
    ) -> str:
        """
        Record user engagement metrics.

        Args:
            metric_type: Type of engagement (e.g., "code_edit_frequency",
                        "question_depth", "time_on_task", "help_seeking_behavior",
                        "persistence_score")
            value: Numeric value for the metric (0.0 - 1.0 for normalized metrics,
                  or actual count for frequency metrics)
            context: Optional context about what triggered this metric

        Returns:
            Confirmation message
        """
        try:
            # Store engagement metric
            engagement_event = {
                "user_id": self.user_id,
                "event_type": "engagement_metric",
                "metric_type": metric_type,
                "value": value,
                "context": context,
                "timestamp": datetime.utcnow()
            }

            await self.db.behavioral_events.insert_one(engagement_event)

            # Update aggregated engagement stats in user profile
            await self.db.user_profiles.update_one(
                {"user_id": self.user_id},
                {
                    "$set": {
                        f"engagement_metrics.{metric_type}": value,
                        "last_active": datetime.utcnow()
                    }
                },
                upsert=True
            )

            print(f"📈 Recorded engagement metric: {metric_type}={value}")

            return f"Successfully recorded engagement metric: {metric_type}={value}"

        except Exception as e:
            print(f"❌ Error recording engagement metric: {str(e)}")
            return f"Error recording engagement metric: {str(e)}"

    async def analyze_error_pattern(
        self,
        error_description: str,
        user_code: str,
        exercise_context: str
    ) -> str:
        """
        Use Claude Haiku to analyze and categorize error patterns.
        Helps identify if errors are syntax, logic, conceptual, or algorithmic.

        Args:
            error_description: Description of the error or failed test
            user_code: The code that produced the error
            exercise_context: What the exercise was asking for

        Returns:
            JSON string with error analysis
        """
        try:
            # Use Claude Haiku for lightweight error analysis
            prompt = f"""Analyze this coding error and categorize it.

Exercise Context: {exercise_context}

User's Code:
```
{user_code}
```

Error/Issue: {error_description}

Categorize this error into ONE of these types:
- "syntax": Missing semicolons, typos, incorrect syntax
- "logic": Wrong algorithm, incorrect conditionals, off-by-one errors
- "conceptual": Misunderstanding of core concept (loops, functions, classes, etc.)
- "algorithmic": Inefficient approach, wrong data structure choice
- "style": Code works but doesn't follow best practices

Also identify:
- The specific concept gap (what concept does the user not understand?)
- Suggested intervention (what should we teach next?)

Respond with ONLY valid JSON in this exact format:
{{
  "error_category": "syntax|logic|conceptual|algorithmic|style",
  "specific_issue": "brief description of the exact issue",
  "concept_gap": "the underlying concept the user needs to learn",
  "severity": "low|medium|high",
  "suggested_intervention": "what to do next (hint, tutorial, simpler exercise, etc.)"
}}"""

            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            response_text = response.content[0].text.strip()
            analysis = json.loads(response_text)

            # Store error pattern
            error_pattern = {
                "user_id": self.user_id,
                "error_category": analysis.get("error_category", "unknown"),
                "specific_issue": analysis.get("specific_issue", ""),
                "concept_gap": analysis.get("concept_gap", ""),
                "severity": analysis.get("severity", "medium"),
                "suggested_intervention": analysis.get("suggested_intervention", ""),
                "user_code": user_code,
                "error_description": error_description,
                "exercise_context": exercise_context,
                "timestamp": datetime.utcnow()
            }

            await self.db.error_patterns.insert_one(error_pattern)

            # Update user profile with concept gap
            concept_gap = analysis.get("concept_gap", "")
            if concept_gap:
                # Add to weak points if not already there
                await self.db.user_profiles.update_one(
                    {
                        "user_id": self.user_id,
                        "weak_points.topic": {"$ne": concept_gap}
                    },
                    {
                        "$push": {
                            "weak_points": {
                                "topic": concept_gap,
                                "description": f"Error pattern: {analysis.get('specific_issue', '')}",
                                "identified_at": datetime.utcnow(),
                                "occurrences": 1,
                                "exercises_failed": [],
                                "last_seen": datetime.utcnow()
                            }
                        }
                    }
                )

            print(f"🔍 Error analysis: {analysis.get('error_category')} - {analysis.get('concept_gap')}")

            return json.dumps(analysis, indent=2)

        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing AI response: {str(e)}")
            # Return fallback analysis
            fallback = {
                "error_category": "unknown",
                "specific_issue": error_description,
                "concept_gap": "Unable to analyze",
                "severity": "medium",
                "suggested_intervention": "Provide hint or ask clarifying question"
            }
            return json.dumps(fallback, indent=2)

        except Exception as e:
            print(f"❌ Error analyzing error pattern: {str(e)}")
            return f'{{"error": "{str(e)}"}}'


def get_tool_definitions() -> list:
    """
    Get tool definitions for the AI to call.
    These will be registered with the Tool Registry.
    """
    return [
        {
            "name": "record_struggle_indicator",
            "description": "Record when you detect the user is struggling. Use this when you observe: repeated requests for hints, long pauses without progress, repeated errors on the same concept, confusion signals in their questions, or signs they're stuck. This helps personalize future content.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "indicator_type": {
                        "type": "string",
                        "description": "Type of struggle: 'repeated_hints', 'long_pause', 'repeated_errors', 'confusion_signal', 'stuck_on_concept', 'frustration_signal'",
                        "enum": ["repeated_hints", "long_pause", "repeated_errors", "confusion_signal", "stuck_on_concept", "frustration_signal"]
                    },
                    "context": {
                        "type": "string",
                        "description": "What is the user struggling with? Be specific (e.g., 'User struggling with for loop syntax after 3 attempts')"
                    },
                    "severity": {
                        "type": "string",
                        "description": "How severe is the struggle? 'low' (minor confusion), 'medium' (needs help), 'high' (very stuck, may give up)",
                        "enum": ["low", "medium", "high"],
                        "default": "medium"
                    }
                },
                "required": ["indicator_type", "context"]
            }
        },
        {
            "name": "record_engagement_metric",
            "description": "Record user engagement metrics you observe during the learning session. Use this to track: how frequently they edit code, depth of their questions, time spent on tasks, help-seeking behavior, persistence. Higher engagement = better learning.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "metric_type": {
                        "type": "string",
                        "description": "Type of engagement metric",
                        "enum": ["code_edit_frequency", "question_depth", "time_on_task", "help_seeking_behavior", "persistence_score", "exploration_level"]
                    },
                    "value": {
                        "type": "number",
                        "description": "Metric value. Use 0.0-1.0 for normalized scores (e.g., persistence_score=0.8 means high persistence), or actual counts for frequency metrics (e.g., code_edit_frequency=15 means 15 edits)"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context about this metric (e.g., 'User asked 5 deep follow-up questions about recursion')"
                    }
                },
                "required": ["metric_type", "value"]
            }
        },
        {
            "name": "analyze_error_pattern",
            "description": "Analyze user's coding error to categorize it and identify concept gaps. Use this when user submits incorrect code or encounters errors. This helps identify whether errors are syntax, logic, conceptual, or algorithmic, and guides intervention strategy.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "error_description": {
                        "type": "string",
                        "description": "Description of the error or failed test (e.g., 'Expected output [1,2,3] but got [1,2]')"
                    },
                    "user_code": {
                        "type": "string",
                        "description": "The code that produced the error"
                    },
                    "exercise_context": {
                        "type": "string",
                        "description": "What was the exercise asking the user to do?"
                    }
                },
                "required": ["error_description", "user_code", "exercise_context"]
            }
        }
    ]
