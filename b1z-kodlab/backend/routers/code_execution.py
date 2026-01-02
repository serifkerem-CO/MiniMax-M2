"""
B1Z KODLAB - Code Execution Router
Safe code execution sandbox
"""
from fastapi import APIRouter, HTTPException
import subprocess
import tempfile
import os
import time
from typing import Dict, Any

from ..models.schemas import CodeExecutionRequest, CodeExecutionResult, ProgrammingLanguage

router = APIRouter(prefix="/execute", tags=["Code Execution"])


def execute_python(code: str, timeout: int) -> Dict[str, Any]:
    """Execute Python code"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        start_time = time.time()
        result = subprocess.run(
            ['python3', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        execution_time = time.time() - start_time

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "execution_time": execution_time
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": None,
            "error": f"Execution timeout ({timeout}s exceeded)",
            "execution_time": timeout
        }
    finally:
        os.unlink(temp_file)


def execute_javascript(code: str, timeout: int) -> Dict[str, Any]:
    """Execute JavaScript code with Node.js"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        start_time = time.time()
        result = subprocess.run(
            ['node', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        execution_time = time.time() - start_time

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "execution_time": execution_time
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": None,
            "error": f"Execution timeout ({timeout}s exceeded)",
            "execution_time": timeout
        }
    except FileNotFoundError:
        return {
            "success": False,
            "output": None,
            "error": "Node.js not installed on server",
            "execution_time": 0
        }
    finally:
        os.unlink(temp_file)


def execute_rust(code: str, timeout: int) -> Dict[str, Any]:
    """Execute Rust code"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        # Compile Rust code
        compile_result = subprocess.run(
            ['rustc', temp_file, '-o', temp_file + '.out'],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if compile_result.returncode != 0:
            return {
                "success": False,
                "output": None,
                "error": f"Compilation error:\n{compile_result.stderr}",
                "execution_time": 0
            }

        # Execute compiled binary
        start_time = time.time()
        result = subprocess.run(
            [temp_file + '.out'],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        execution_time = time.time() - start_time

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "execution_time": execution_time
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": None,
            "error": f"Execution timeout ({timeout}s exceeded)",
            "execution_time": timeout
        }
    except FileNotFoundError:
        return {
            "success": False,
            "output": None,
            "error": "Rust compiler not installed on server",
            "execution_time": 0
        }
    finally:
        os.unlink(temp_file)
        if os.path.exists(temp_file + '.out'):
            os.unlink(temp_file + '.out')


@router.post("/run", response_model=CodeExecutionResult)
async def execute_code(request: CodeExecutionRequest):
    """
    Execute code safely in sandbox
    Supports Python, JavaScript, Rust, Go
    """
    executors = {
        ProgrammingLanguage.PYTHON: execute_python,
        ProgrammingLanguage.JAVASCRIPT: execute_javascript,
        ProgrammingLanguage.TYPESCRIPT: execute_javascript,  # Transpile first in production
        ProgrammingLanguage.RUST: execute_rust,
        # ProgrammingLanguage.GO: execute_go,  # Implement as needed
    }

    if request.language not in executors:
        raise HTTPException(
            status_code=400,
            detail=f"Language {request.language} not yet supported for execution"
        )

    try:
        result = executors[request.language](request.code, request.timeout)
        return CodeExecutionResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/health")
async def check_execution_health():
    """Check which language runtimes are available"""
    runtimes = {}

    # Check Python
    try:
        subprocess.run(['python3', '--version'], capture_output=True, timeout=1)
        runtimes['python'] = True
    except:
        runtimes['python'] = False

    # Check Node.js
    try:
        subprocess.run(['node', '--version'], capture_output=True, timeout=1)
        runtimes['javascript'] = True
    except:
        runtimes['javascript'] = False

    # Check Rust
    try:
        subprocess.run(['rustc', '--version'], capture_output=True, timeout=1)
        runtimes['rust'] = True
    except:
        runtimes['rust'] = False

    # Check Go
    try:
        subprocess.run(['go', 'version'], capture_output=True, timeout=1)
        runtimes['go'] = True
    except:
        runtimes['go'] = False

    return {
        "status": "healthy",
        "available_runtimes": runtimes
    }
