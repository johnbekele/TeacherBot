"""
Exercise grading service
"""
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
# Use subprocess sandbox instead of Docker for development
from app.sandbox.subprocess_runner import sandbox
from app.sandbox.validators.test_validator import validate_test_cases, calculate_score
from app.models.exercise import ExecutionResult, TestResult


async def grade_exercise(
    db: AsyncIOMotorDatabase,
    submission_id: str,
    exercise_id: str,
    code: str,
    language: str
) -> dict:
    """
    Grade an exercise submission

    Args:
        db: Database instance
        submission_id: Submission ID
        exercise_id: Exercise ID
        code: Submitted code
        language: Programming language

    Returns:
        Grading result dictionary
    """

    # Get exercise from database
    exercise = await db.exercises.find_one({"exercise_id": exercise_id})
    if not exercise:
        return {
            "error": "Exercise not found",
            "score": 0,
            "passed": False
        }

    # Build complete code with validation scripts
    # For exercises with validation scripts, append them to execute the functions
    complete_code = code
    test_cases = exercise.get("test_cases", [])

    # If there are validation scripts, append them to call the user's functions
    if test_cases and test_cases[0].get("validation_script"):
        validation_script = test_cases[0].get("validation_script")
        complete_code = f"{code}\n\n# Test execution\n{validation_script}"

    # Execute code in sandbox
    exec_result = sandbox.execute_code(complete_code, language)

    execution_result = ExecutionResult(
        stdout=exec_result["stdout"],
        stderr=exec_result["stderr"],
        exit_code=exec_result["exit_code"],
        execution_time=exec_result["execution_time"]
    )

    # Validate test cases
    test_cases = [tc for tc in exercise.get("test_cases", [])]
    test_results = validate_test_cases(execution_result, test_cases, language)

    # Calculate score
    score = calculate_score(test_results)
    passed = score >= 70  # Passing threshold

    # Generate feedback
    feedback = generate_feedback(test_results, score, passed)

    # Update attempt in database
    await db.exercise_attempts.update_one(
        {"_id": ObjectId(submission_id)},
        {
            "$set": {
                "execution_result": execution_result.dict(),
                "test_results": [tr.dict() for tr in test_results],
                "score": score,
                "feedback": feedback,
                "graded_at": datetime.utcnow()
            }
        }
    )

    return {
        "submission_id": submission_id,
        "score": score,
        "passed": passed,
        "test_results": test_results,
        "feedback": feedback,
        "execution_result": execution_result
    }


def generate_feedback(
    test_results: list[TestResult],
    score: int,
    passed: bool
) -> str:
    """Generate human-readable feedback"""

    total_tests = len(test_results)
    passed_tests = sum(1 for tr in test_results if tr.passed)

    if passed:
        feedback = f"🎉 Great job! You passed all {passed_tests}/{total_tests} test cases.\n\n"
        feedback += "Your solution is correct. Ready to move on to the next exercise!"
    elif passed_tests == 0:
        feedback = f"❌ None of the test cases passed ({passed_tests}/{total_tests}).\n\n"
        feedback += "Let's review the requirements:\n"
        for tr in test_results:
            if not tr.passed:
                feedback += f"- {tr.test_id}: {tr.error_message}\n"
        feedback += "\nTip: Try running your code locally first to see the output."
    else:
        feedback = f"⚠️  Some test cases passed ({passed_tests}/{total_tests}), but not all.\n\n"
        feedback += "Failed tests:\n"
        for tr in test_results:
            if not tr.passed:
                feedback += f"- {tr.test_id}: {tr.error_message}\n"
        feedback += "\nYou're close! Review the failed test cases and try again."

    return feedback
