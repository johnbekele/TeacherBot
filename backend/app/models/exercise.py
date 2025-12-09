from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class Hint(BaseModel):
    """Exercise hint"""
    hint_number: int
    text: str
    reveal_after_attempts: int = 1


class TestCase(BaseModel):
    """Exercise test case"""
    test_id: str
    description: str
    input: Dict[str, Any] = {}
    expected_output: Dict[str, Any] = {}
    validation_script: str


class GradingRubric(BaseModel):
    """Grading criteria weights"""
    correctness_weight: float = 0.7
    style_weight: float = 0.2
    efficiency_weight: float = 0.1


class ExerciseBase(BaseModel):
    """Base exercise model"""
    exercise_id: str
    node_id: str
    title: str
    description: str
    type: str  # python, bash, terraform, pulumi, ansible
    difficulty: str  # beginner, intermediate, advanced
    prompt: str
    starter_code: str = ""


class ExerciseCreate(ExerciseBase):
    """Exercise creation model"""
    solution: str
    hints: List[Hint] = []
    test_cases: List[TestCase] = []
    grading_rubric: GradingRubric = Field(default_factory=GradingRubric)


class ExerciseInDB(ExerciseCreate):
    """Exercise model in database"""
    id: Optional[str] = Field(alias="_id", default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ExerciseResponse(ExerciseBase):
    """Exercise response (without solution)"""
    id: str = Field(alias="_id")
    hints_available: int = 0

    class Config:
        populate_by_name = True


class ExecutionResult(BaseModel):
    """Code execution result"""
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float


class TestResult(BaseModel):
    """Individual test result"""
    test_id: str
    passed: bool
    actual_output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ExerciseSubmit(BaseModel):
    """Exercise submission"""
    code: str = Field(..., max_length=10000)
    language: str


class ExerciseAttemptInDB(BaseModel):
    """Exercise attempt in database"""
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    exercise_id: str
    attempt_number: int
    submitted_code: str
    execution_result: Optional[ExecutionResult] = None
    test_results: List[TestResult] = []
    score: int = 0
    feedback: str = ""
    ai_comments: str = ""
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    graded_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ExerciseResultResponse(BaseModel):
    """Exercise result response"""
    submission_id: str
    status: str  # grading, completed, failed
    score: int = 0
    passed: bool = False
    test_results: List[TestResult] = []
    feedback: str = ""
    next_step: str = ""
    hints_available: int = 0
