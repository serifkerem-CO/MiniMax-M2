# MiniMax-M2 Coding Assistant Template

A powerful coding assistant that can analyze, write, and modify code using MiniMax-M2.

MiniMax-M2 ranks **#1 among open-source models** on coding benchmarks:
- SWE-bench Verified: **69.4%**
- Terminal-Bench: **46.3%**
- LiveCodeBench: **83%**

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your API settings in `main.py`

3. Run the assistant:
```bash
python main.py
```

## Features

- **Code Analysis**: Understand and evaluate code quality
- **Code Generation**: Write code from descriptions
- **Bug Fixing**: Fix code based on error messages
- **Refactoring**: Improve code structure and quality
- **Code Review**: Get detailed feedback on code
- **Code Explanation**: Understand how code works
- **Multi-language Support**: Python, JavaScript, TypeScript, Go, Rust, and more

## Commands

| Command | Description |
|---------|-------------|
| `/load <path>` | Load a file into workspace |
| `/analyze` | Analyze loaded code |
| `/write <desc>` | Generate code from description |
| `/fix` | Fix code with error |
| `/refactor` | Refactor loaded code |
| `/explain` | Explain loaded code |
| `/review` | Perform code review |
| `/run` | Run Python code |
| `/clear` | Clear conversation |
| `/quit` | Exit |

## Usage Examples

### Generate Code
```
You: /write a function to merge two sorted lists efficiently
```

### Load and Analyze
```
You: /load ./mycode.py
You: /analyze
```

### Fix an Error
```python
from coding_assistant import CodingAssistant

assistant = CodingAssistant()

code = """
def divide(a, b):
    return a / b
"""

error = "ZeroDivisionError: division by zero"

fixed = assistant.fix_code(code, error)
print(fixed)
```

### Code Review
```python
assistant = CodingAssistant()
assistant.load_file("./myproject/main.py")
review = assistant.code_review(code, "python")
print(review)
```

## Thinking Mode

MiniMax-M2 uses interleaved thinking with `<think>...</think>` tags for complex reasoning. This helps provide more accurate and well-thought-out solutions for challenging coding problems.

## Best Practices

1. **Provide Context**: Load relevant files before asking questions
2. **Be Specific**: Clear descriptions lead to better code generation
3. **Iterate**: Use conversation history to refine solutions
4. **Review Output**: Always review generated code before using in production
