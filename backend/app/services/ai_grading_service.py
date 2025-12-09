"""
AI-Powered Grading Service using Claude Sonnet
Provides structured, rubric-based assessment of student code submissions
"""
from anthropic import AsyncAnthropic
from app.config import get_settings
import json
from typing import Dict, List, Optional

settings = get_settings()


class AIGradingService:
    """Service for AI-powered code assessment with detailed feedback"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def grade_submission(
        self,
        exercise: Dict,
        student_code: str,
        expected_solution: Optional[str] = None
    ) -> Dict:
        """
        Grade a student's code submission using AI with structured rubric.

        Args:
            exercise: Exercise details (title, description, prompt, type)
            student_code: The code submitted by the student
            expected_solution: Optional reference solution for comparison

        Returns:
            Dict with:
                - score: int (0-100)
                - passed: bool (score >= 70)
                - breakdown: dict with correctness, quality, efficiency scores
                - feedback: dict with strengths, improvements, suggestions
                - categorized_issues: list of specific issues found
                - next_steps: what student should do next
        """

        # Build grading prompt with rubric
        prompt = self._build_grading_prompt(exercise, student_code, expected_solution)

        try:
            # Use Claude Sonnet for intelligent grading
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for consistent grading
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse structured response
            response_text = response.content[0].text.strip()

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            grading_result = json.loads(response_text)

            # Validate and normalize result
            result = self._normalize_grading_result(grading_result)

            print(f"✅ AI Grading: {result['score']}/100 - {result['feedback']['summary'][:50]}...")

            return result

        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error in AI grading: {str(e)}")
            return self._fallback_grading(student_code)

        except Exception as e:
            print(f"❌ AI grading error: {str(e)}")
            return self._fallback_grading(student_code)

    def _build_grading_prompt(
        self,
        exercise: Dict,
        student_code: str,
        expected_solution: Optional[str]
    ) -> str:
        """Build the grading prompt with rubric"""

        exercise_type = exercise.get("type", "python")
        title = exercise.get("title", "Exercise")
        description = exercise.get("description", "")
        prompt = exercise.get("prompt", "")

        base_prompt = f"""You are an expert programming instructor grading a student's code submission.

## Exercise Details
**Title:** {title}
**Type:** {exercise_type}
**Description:** {description}
**Task:** {prompt}

## Student's Code
```{exercise_type}
{student_code}
```
"""

        if expected_solution:
            base_prompt += f"""
## Reference Solution
```{exercise_type}
{expected_solution}
```
"""

        base_prompt += """
## Grading Rubric
Evaluate the code across these dimensions:

1. **Correctness (40%)** - Does it solve the problem?
   - Logic is sound and produces correct outputs
   - Handles edge cases appropriately
   - No runtime errors

2. **Code Quality (30%)** - Is it well-written?
   - Clean, readable code with good naming
   - Proper structure and organization
   - Follows language conventions

3. **Efficiency (20%)** - Is it performant?
   - Uses appropriate algorithms/data structures
   - Avoids unnecessary operations
   - Reasonable time/space complexity

4. **Best Practices (10%)** - Does it follow standards?
   - Error handling where needed
   - Documentation/comments if complex
   - No security issues or bad patterns

## Output Format
Respond with ONLY valid JSON in this exact structure:
```json
{
  "score": 85,
  "breakdown": {
    "correctness": 90,
    "quality": 85,
    "efficiency": 80,
    "best_practices": 85
  },
  "feedback": {
    "summary": "Brief 1-sentence overall assessment",
    "strengths": ["What they did well", "Another strength"],
    "improvements": ["What needs work", "Another improvement"],
    "specific_issues": [
      {
        "type": "correctness|quality|efficiency|best_practices",
        "severity": "low|medium|high",
        "description": "Specific issue description",
        "line_reference": "Which part of code (if applicable)"
      }
    ]
  },
  "next_steps": "What the student should do next (revise, move on, review concept, etc.)"
}
```

Be constructive and encouraging while being honest about issues. Focus on learning, not just scoring.
"""

        return base_prompt

    def _normalize_grading_result(self, result: Dict) -> Dict:
        """Normalize and validate grading result"""

        # Ensure score is within bounds
        score = max(0, min(100, result.get("score", 50)))

        # Ensure breakdown exists
        breakdown = result.get("breakdown", {})
        breakdown = {
            "correctness": max(0, min(100, breakdown.get("correctness", 50))),
            "quality": max(0, min(100, breakdown.get("quality", 50))),
            "efficiency": max(0, min(100, breakdown.get("efficiency", 50))),
            "best_practices": max(0, min(100, breakdown.get("best_practices", 50)))
        }

        # Ensure feedback exists
        feedback = result.get("feedback", {})
        feedback = {
            "summary": feedback.get("summary", "Code submitted for review"),
            "strengths": feedback.get("strengths", []),
            "improvements": feedback.get("improvements", []),
            "specific_issues": feedback.get("specific_issues", [])
        }

        # Ensure next_steps exists
        next_steps = result.get("next_steps", "Review feedback and try again" if score < 70 else "Continue to next exercise")

        return {
            "score": score,
            "passed": score >= 70,
            "breakdown": breakdown,
            "feedback": feedback,
            "next_steps": next_steps,
            "graded_by": "ai_sonnet"
        }

    def _fallback_grading(self, student_code: str) -> Dict:
        """Fallback to heuristic grading if AI fails"""

        print("⚠️ Using fallback heuristic grading")

        code = student_code.strip()
        score = 50  # Default

        # Basic heuristics
        if len(code) < 10:
            score = 30
        elif any(keyword in code for keyword in ['def ', 'function ', 'const ', 'let ', 'var ']):
            score = 70
            if 'return' in code:
                score = 80
            if any(keyword in code for keyword in ['if ', 'for ', 'while ']):
                score = 85

        return {
            "score": score,
            "passed": score >= 70,
            "breakdown": {
                "correctness": score,
                "quality": score - 5,
                "efficiency": score - 10,
                "best_practices": score - 5
            },
            "feedback": {
                "summary": "Code assessed with basic heuristics",
                "strengths": ["Code submitted"],
                "improvements": ["Detailed AI grading unavailable"],
                "specific_issues": []
            },
            "next_steps": "Review code and try again" if score < 70 else "Continue",
            "graded_by": "fallback_heuristic"
        }


async def grade_exercise(
    exercise: Dict,
    student_code: str,
    expected_solution: Optional[str] = None
) -> Dict:
    """
    Convenience function for grading an exercise submission.

    Args:
        exercise: Exercise details
        student_code: Student's submitted code
        expected_solution: Optional reference solution

    Returns:
        Grading result dictionary
    """
    service = AIGradingService()
    return await service.grade_submission(exercise, student_code, expected_solution)
