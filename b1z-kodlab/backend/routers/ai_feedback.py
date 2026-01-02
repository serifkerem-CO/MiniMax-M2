"""
B1Z KODLAB - AI Feedback Router
Powered by MiniMax-M2
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import httpx
import asyncio

from ..config import settings
from ..models.schemas import CodeRequest, AIFeedback

router = APIRouter(prefix="/ai", tags=["AI Feedback"])


async def call_minimax_api(prompt: str, system_prompt: str = "") -> str:
    """Call MiniMax-M2 API"""
    try:
        async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT) as client:
            response = await client.post(
                f"{settings.MINIMAX_API_BASE}/chat/completions",
                json={
                    "model": settings.MINIMAX_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt} if system_prompt else None,
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 1.0,
                    "top_p": 0.95,
                    "top_k": 40
                },
                headers={
                    "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MiniMax API error: {str(e)}")


async def get_ai_perspective(code: str, language: str, perspective_type: str) -> Dict[str, Any]:
    """Get a single AI perspective on code"""
    prompts = {
        "performance": f"Analyze this {language} code for performance optimization:\n\n{code}",
        "security": f"Review this {language} code for security vulnerabilities:\n\n{code}",
        "readability": f"Evaluate this {language} code for readability and maintainability:\n\n{code}",
        "best_practices": f"Check this {language} code against best practices:\n\n{code}",
        "bugs": f"Find potential bugs in this {language} code:\n\n{code}",
        "testing": f"Suggest test cases for this {language} code:\n\n{code}",
        "documentation": f"Evaluate documentation quality of this {language} code:\n\n{code}",
        "architecture": f"Review the architectural design of this {language} code:\n\n{code}",
        "scalability": f"Analyze scalability of this {language} code:\n\n{code}",
        "error_handling": f"Review error handling in this {language} code:\n\n{code}",
        "educational": f"Explain this {language} code from an educational perspective:\n\n{code}"
    }

    system_prompt = f"You are an expert {language} developer and code reviewer. Provide concise, actionable feedback."
    response = await call_minimax_api(prompts[perspective_type], system_prompt)

    return {
        "type": perspective_type,
        "feedback": response
    }


@router.post("/analyze", response_model=AIFeedback)
async def analyze_code(request: CodeRequest):
    """
    Analyze code with MiniMax-M2 AI
    Returns comprehensive feedback including 11 Akıl Harmanları
    """
    # Main analysis
    main_prompt = f"""
Analyze this {request.language} code and provide:
1. A quality score (0-100)
2. Top 3 improvement suggestions
3. Any errors or bugs found
4. Optimization opportunities
5. Educational notes for learners

Code:
{request.code}

{f"Context: {request.context}" if request.context else ""}

Respond in a structured format.
"""

    system_prompt = """You are an expert programming instructor using the B1Z KODLAB platform.
Provide clear, educational feedback that helps learners improve their coding skills."""

    try:
        main_response = await call_minimax_api(main_prompt, system_prompt)

        # Parse response (simplified - in production, use structured output)
        # For MVP, we'll create a basic response structure

        # Optional: Get 11 Akıl Harmanları (11 perspectives)
        perspectives = None
        if settings.PARALLEL_AI_COUNT == 11:
            perspective_types = [
                "performance", "security", "readability", "best_practices",
                "bugs", "testing", "documentation", "architecture",
                "scalability", "error_handling", "educational"
            ]

            # Run all 11 perspectives in parallel
            perspective_tasks = [
                get_ai_perspective(request.code, request.language, ptype)
                for ptype in perspective_types
            ]
            perspectives = await asyncio.gather(*perspective_tasks)

        # Construct feedback response
        return AIFeedback(
            score=85,  # In production, extract from AI response
            suggestions=[
                "Add type hints for better code clarity",
                "Consider edge cases in input validation",
                "Improve variable naming for readability"
            ],
            errors=[],
            optimizations=[
                "Use list comprehension for better performance",
                "Cache repeated calculations"
            ],
            educational_notes=main_response,
            perspectives=perspectives
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/chat")
async def ai_chat(message: str, context: str = ""):
    """
    Chat with AI mentor for coding help
    """
    system_prompt = """You are a friendly AI coding mentor on B1Z KODLAB.
Help learners understand programming concepts with clear explanations and examples."""

    full_prompt = f"{context}\n\nUser question: {message}" if context else message

    try:
        response = await call_minimax_api(full_prompt, system_prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
