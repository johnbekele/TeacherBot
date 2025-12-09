"""
Test case validation logic
"""
from typing import Dict, List, Any
from app.models.exercise import TestCase, TestResult, ExecutionResult


def validate_test_cases(
    execution_result: ExecutionResult,
    test_cases: List[Any],  # Can be dict or TestCase
    language: str
) -> List[TestResult]:
    """
    Validate execution results against test cases

    Args:
        execution_result: Result from sandbox execution
        test_cases: List of test cases to validate (dicts or TestCase objects)
        language: Programming language

    Returns:
        List of test results
    """
    results = []

    # If execution failed, all tests fail
    if execution_result.exit_code != 0:
        for i, test_case in enumerate(test_cases):
            test_id = test_case.get("test_id", f"test_{i}") if isinstance(test_case, dict) else test_case.test_id
            results.append(TestResult(
                test_id=test_id,
                passed=False,
                error_message=f"Execution failed: {execution_result.stderr}"
            ))
        return results

    # Validate each test case
    for test_case in test_cases:
        result = validate_single_test(
            execution_result,
            test_case,
            language
        )
        results.append(result)

    return results


def validate_single_test(
    execution_result: ExecutionResult,
    test_case: Any,  # Can be dict or TestCase
    language: str
) -> TestResult:
    """Validate a single test case"""

    try:
        # Handle both dict and TestCase object
        if isinstance(test_case, dict):
            test_id = test_case.get("test_id", "test_1")
            expected_output = test_case.get("expected_output", {})
        else:
            test_id = test_case.test_id
            expected_output = test_case.expected_output

        # Check expected output
        expected_stdout = expected_output.get("stdout", "") if isinstance(expected_output, dict) else ""
        actual_stdout = execution_result.stdout

        # Simple string comparison
        if expected_stdout:
            if actual_stdout.strip() == expected_stdout.strip():
                return TestResult(
                    test_id=test_id,
                    passed=True,
                    actual_output={"stdout": actual_stdout}
                )
            else:
                return TestResult(
                    test_id=test_id,
                    passed=False,
                    actual_output={"stdout": actual_stdout},
                    error_message=f"Expected: '{expected_stdout}', Got: '{actual_stdout}'"
                )

        # If no specific output expected, check exit code
        if execution_result.exit_code == 0:
            return TestResult(
                test_id=test_id,
                passed=True,
                actual_output={"stdout": actual_stdout}
            )
        else:
            return TestResult(
                test_id=test_id,
                passed=False,
                actual_output={"stdout": actual_stdout},
                error_message="Non-zero exit code"
            )

    except Exception as e:
        test_id = test_case.get("test_id", "test_error") if isinstance(test_case, dict) else "test_error"
        return TestResult(
            test_id=test_id,
            passed=False,
            error_message=f"Validation error: {str(e)}"
        )


def calculate_score(test_results: List[TestResult]) -> int:
    """
    Calculate score based on test results

    Args:
        test_results: List of test results

    Returns:
        Score out of 100
    """
    if not test_results:
        return 0

    passed = sum(1 for r in test_results if r.passed)
    total = len(test_results)

    return int((passed / total) * 100)
