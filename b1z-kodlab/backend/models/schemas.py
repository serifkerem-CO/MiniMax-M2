"""
B1Z KODLAB - Data Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ProgrammingLanguage(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    GO = "go"
    CPP = "cpp"


class CodeRequest(BaseModel):
    """Request to analyze/execute code"""
    code: str = Field(..., description="Source code to analyze")
    language: ProgrammingLanguage = Field(..., description="Programming language")
    context: Optional[str] = Field(None, description="Additional context for AI")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "def fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
                "language": "python",
                "context": "This is a recursive fibonacci implementation"
            }
        }


class AIFeedback(BaseModel):
    """AI feedback on code"""
    score: int = Field(..., ge=0, le=100, description="Code quality score (0-100)")
    suggestions: List[str] = Field(..., description="Improvement suggestions")
    errors: List[str] = Field(default_factory=list, description="Detected errors")
    optimizations: List[str] = Field(default_factory=list, description="Optimization tips")
    educational_notes: str = Field(..., description="Educational explanation")

    # 11 Akıl Harmanları
    perspectives: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="11 different AI perspectives on the code"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "score": 75,
                "suggestions": [
                    "Consider using memoization to optimize recursive calls",
                    "Add type hints for better code clarity"
                ],
                "errors": [],
                "optimizations": [
                    "Use iterative approach for better performance",
                    "Implement dynamic programming solution"
                ],
                "educational_notes": "Recursive fibonacci has O(2^n) complexity. Consider optimization."
            }
        }


class LessonModule(BaseModel):
    """Learning module/lesson"""
    id: int
    title: str
    description: str
    language: ProgrammingLanguage
    difficulty: int = Field(..., ge=1, le=11, description="Difficulty level (1-11)")
    content: str
    exercises: List[str]
    points: int = Field(default=111, description="Points awarded for completion")


class UserProgress(BaseModel):
    """User learning progress"""
    user_id: str
    completed_lessons: List[int] = Field(default_factory=list)
    total_points: int = Field(default=0, description="B1Z points earned")
    streak_days: int = Field(default=0, description="Consecutive learning days")
    level: int = Field(default=1, description="User level")


class CodeExecutionRequest(BaseModel):
    """Request to execute code"""
    code: str
    language: ProgrammingLanguage
    test_cases: Optional[List[Dict[str, Any]]] = None
    timeout: int = Field(default=5, ge=1, le=30, description="Execution timeout in seconds")


class CodeExecutionResult(BaseModel):
    """Result of code execution"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
    test_results: Optional[List[Dict[str, Any]]] = None
