"""
B1Z KODLAB - Lessons Router
11 Learning Modules
"""
from fastapi import APIRouter, HTTPException
from typing import List
import os
import json

from ..models.schemas import LessonModule, ProgrammingLanguage

router = APIRouter(prefix="/lessons", tags=["Lessons"])

# İlk 11 ders - B1Z KODLAB Curriculum
LESSONS_DATA = [
    {
        "id": 1,
        "title": "Python Temelleri",
        "description": "Python programlamaya giriş: değişkenler, veri tipleri, kontrol yapıları",
        "language": ProgrammingLanguage.PYTHON,
        "difficulty": 1,
        "content": "lessons/01-python-basics.md",
        "exercises": [
            "Fibonacci dizisi oluştur",
            "Asal sayı kontrolü yap",
            "Liste comprehension kullan"
        ],
        "points": 111
    },
    {
        "id": 2,
        "title": "JavaScript/TypeScript Basics",
        "description": "Modern JavaScript ve TypeScript temelleri",
        "language": ProgrammingLanguage.JAVASCRIPT,
        "difficulty": 2,
        "content": "lessons/02-javascript-basics.md",
        "exercises": [
            "Arrow function kullanımı",
            "Promise ve async/await",
            "Type annotations (TypeScript)"
        ],
        "points": 111
    },
    {
        "id": 3,
        "title": "Rust Fundamentals",
        "description": "Sistem programlama ve Rust'a giriş",
        "language": ProgrammingLanguage.RUST,
        "difficulty": 3,
        "content": "lessons/03-rust-fundamentals.md",
        "exercises": [
            "Ownership ve borrowing",
            "Pattern matching",
            "Error handling with Result"
        ],
        "points": 111
    },
    {
        "id": 4,
        "title": "Go ile Backend",
        "description": "Go dilinde backend geliştirme",
        "language": ProgrammingLanguage.GO,
        "difficulty": 4,
        "content": "lessons/04-go-backend.md",
        "exercises": [
            "HTTP server oluştur",
            "Goroutines kullan",
            "Channels ile haberleşme"
        ],
        "points": 111
    },
    {
        "id": 5,
        "title": "React ile Frontend",
        "description": "Modern React ile kullanıcı arayüzü geliştirme",
        "language": ProgrammingLanguage.JAVASCRIPT,
        "difficulty": 5,
        "content": "lessons/05-react-frontend.md",
        "exercises": [
            "Component oluştur",
            "Hooks kullan (useState, useEffect)",
            "Props ve state yönetimi"
        ],
        "points": 111
    },
    {
        "id": 6,
        "title": "FastAPI ile API",
        "description": "Python FastAPI ile RESTful API geliştirme",
        "language": ProgrammingLanguage.PYTHON,
        "difficulty": 6,
        "content": "lessons/06-fastapi-api.md",
        "exercises": [
            "CRUD endpoints oluştur",
            "Pydantic modelleri kullan",
            "Authentication ekle"
        ],
        "points": 111
    },
    {
        "id": 7,
        "title": "Git ve GitHub",
        "description": "Versiyon kontrolü ve işbirliği",
        "language": ProgrammingLanguage.PYTHON,
        "difficulty": 3,
        "content": "lessons/07-git-github.md",
        "exercises": [
            "Repository oluştur",
            "Branch ve merge işlemleri",
            "Pull request aç"
        ],
        "points": 111
    },
    {
        "id": 8,
        "title": "Docker Konteyner",
        "description": "Konteynerizasyon ve Docker",
        "language": ProgrammingLanguage.PYTHON,
        "difficulty": 7,
        "content": "lessons/08-docker-container.md",
        "exercises": [
            "Dockerfile yaz",
            "Multi-stage build kullan",
            "Docker Compose ile orchestration"
        ],
        "points": 111
    },
    {
        "id": 9,
        "title": "AI Tool Calling (MiniMax-M2)",
        "description": "AI modellerini kullanarak tool calling",
        "language": ProgrammingLanguage.PYTHON,
        "difficulty": 8,
        "content": "lessons/09-ai-tool-calling.md",
        "exercises": [
            "MiniMax-M2 API entegrasyonu",
            "Function calling implement et",
            "Multi-agent sistem kur"
        ],
        "points": 111
    },
    {
        "id": 10,
        "title": "Test Driven Development",
        "description": "TDD ile kaliteli kod yazma",
        "language": ProgrammingLanguage.PYTHON,
        "difficulty": 9,
        "content": "lessons/10-tdd.md",
        "exercises": [
            "Unit test yaz (pytest)",
            "Test coverage artır",
            "Mocking ve fixtures kullan"
        ],
        "points": 111
    },
    {
        "id": 11,
        "title": "Deploy ve CI/CD",
        "description": "Continuous Integration ve Deployment",
        "language": ProgrammingLanguage.PYTHON,
        "difficulty": 11,
        "content": "lessons/11-deploy-cicd.md",
        "exercises": [
            "GitHub Actions workflow yaz",
            "Automated testing setup",
            "Production deploy"
        ],
        "points": 1111  # Special: 1111 points for mastery!
    }
]


@router.get("/", response_model=List[LessonModule])
async def get_all_lessons():
    """Get all 11 learning modules"""
    return LESSONS_DATA


@router.get("/{lesson_id}", response_model=LessonModule)
async def get_lesson(lesson_id: int):
    """Get specific lesson by ID"""
    lesson = next((l for l in LESSONS_DATA if l["id"] == lesson_id), None)
    if not lesson:
        raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")
    return lesson


@router.get("/language/{language}")
async def get_lessons_by_language(language: ProgrammingLanguage):
    """Get all lessons for a specific programming language"""
    filtered = [l for l in LESSONS_DATA if l["language"] == language]
    return filtered


@router.get("/difficulty/{level}")
async def get_lessons_by_difficulty(level: int):
    """Get lessons by difficulty level (1-11)"""
    if level < 1 or level > 11:
        raise HTTPException(status_code=400, detail="Difficulty must be between 1 and 11")
    filtered = [l for l in LESSONS_DATA if l["difficulty"] == level]
    return filtered
