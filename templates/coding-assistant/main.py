"""
MiniMax-M2 Coding Assistant Template
====================================
A template for building a coding assistant that can analyze, write,
and modify code using MiniMax-M2.

MiniMax-M2 ranks #1 among open-source models on coding benchmarks like
SWE-bench (69.4%) and Terminal-Bench (46.3%).

Requirements:
    pip install openai rich

Usage:
    python main.py
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from openai import OpenAI

try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Configuration
API_BASE_URL = "http://localhost:8000/v1"
API_KEY = "your-api-key-here"
MODEL_NAME = "MiniMax-M2"


@dataclass
class CodeFile:
    """Represents a code file with its content."""
    path: str
    content: str
    language: str


class CodingAssistant:
    """A coding assistant powered by MiniMax-M2."""

    SYSTEM_PROMPT = """You are an expert coding assistant powered by MiniMax-M2.
You excel at:
- Analyzing and understanding code in any language
- Writing clean, efficient, and well-documented code
- Debugging and fixing issues
- Refactoring and optimizing code
- Explaining complex code concepts

When providing code:
- Use appropriate language-specific best practices
- Include helpful comments for complex logic
- Consider edge cases and error handling
- Suggest tests when appropriate

Use <think>...</think> tags for your reasoning process before providing solutions."""

    def __init__(self, api_key: str = API_KEY, base_url: str = API_BASE_URL):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.messages = []
        self.console = Console() if RICH_AVAILABLE else None
        self.workspace_files: dict[str, CodeFile] = {}

    def _print(self, text: str, style: str = None):
        """Print text with optional styling."""
        if self.console:
            self.console.print(text, style=style)
        else:
            print(text)

    def _print_code(self, code: str, language: str = "python"):
        """Print code with syntax highlighting."""
        if self.console:
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            self.console.print(syntax)
        else:
            print(f"```{language}\n{code}\n```")

    def reset(self):
        """Reset conversation and workspace."""
        self.messages = []
        self.workspace_files = {}

    def load_file(self, path: str) -> Optional[CodeFile]:
        """Load a file into the workspace."""
        try:
            file_path = Path(path)
            content = file_path.read_text()
            language = self._detect_language(file_path.suffix)
            code_file = CodeFile(
                path=str(file_path.absolute()),
                content=content,
                language=language
            )
            self.workspace_files[path] = code_file
            return code_file
        except Exception as e:
            self._print(f"Error loading file: {e}", style="red")
            return None

    def _detect_language(self, suffix: str) -> str:
        """Detect programming language from file extension."""
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
        }
        return mapping.get(suffix.lower(), "text")

    def _build_context(self) -> str:
        """Build context from loaded workspace files."""
        if not self.workspace_files:
            return ""

        context_parts = ["<workspace_files>"]
        for path, code_file in self.workspace_files.items():
            context_parts.append(f"<file path=\"{path}\" language=\"{code_file.language}\">")
            context_parts.append(code_file.content)
            context_parts.append("</file>")
        context_parts.append("</workspace_files>")

        return "\n".join(context_parts)

    def ask(self, question: str, include_workspace: bool = True) -> str:
        """
        Ask the coding assistant a question.

        Args:
            question: The coding question or request
            include_workspace: Whether to include loaded files as context

        Returns:
            The assistant's response
        """
        # Build system message with context
        system_content = self.SYSTEM_PROMPT
        if include_workspace and self.workspace_files:
            system_content += "\n\n" + self._build_context()

        # Initialize or update system message
        if not self.messages:
            self.messages.append({
                "role": "system",
                "content": system_content
            })
        else:
            self.messages[0]["content"] = system_content

        # Add user question
        self.messages.append({
            "role": "user",
            "content": question
        })

        # Get response
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=self.messages,
            temperature=0.3,  # Lower temperature for more precise code
            max_tokens=4096,
        )

        assistant_message = response.choices[0].message.content

        # Add to history
        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def analyze_code(self, code: str, language: str = "python") -> str:
        """Analyze a code snippet."""
        prompt = f"""Analyze the following {language} code:

```{language}
{code}
```

Provide:
1. A brief summary of what the code does
2. Code quality assessment
3. Potential issues or bugs
4. Suggestions for improvement"""

        return self.ask(prompt, include_workspace=False)

    def write_code(self, description: str, language: str = "python") -> str:
        """Generate code based on a description."""
        prompt = f"""Write {language} code that does the following:

{description}

Requirements:
- Follow {language} best practices
- Include appropriate error handling
- Add clear comments for complex logic
- Make the code production-ready"""

        return self.ask(prompt, include_workspace=False)

    def fix_code(self, code: str, error: str, language: str = "python") -> str:
        """Fix code based on an error message."""
        prompt = f"""Fix the following {language} code that produces this error:

Error:
```
{error}
```

Code:
```{language}
{code}
```

Provide the fixed code and explain what was wrong."""

        return self.ask(prompt, include_workspace=False)

    def refactor_code(self, code: str, language: str = "python", goals: str = "") -> str:
        """Refactor code with optional goals."""
        goals_text = f"\n\nRefactoring goals:\n{goals}" if goals else ""

        prompt = f"""Refactor the following {language} code to improve its quality:{goals_text}

```{language}
{code}
```

Provide:
1. The refactored code
2. Explanation of changes made
3. Benefits of the refactoring"""

        return self.ask(prompt, include_workspace=False)

    def explain_code(self, code: str, language: str = "python") -> str:
        """Explain how code works."""
        prompt = f"""Explain the following {language} code in detail:

```{language}
{code}
```

Provide:
1. High-level overview
2. Line-by-line explanation of key parts
3. Any important concepts or patterns used"""

        return self.ask(prompt, include_workspace=False)

    def run_code(self, code: str, language: str = "python") -> tuple[str, str]:
        """
        Run code and return stdout and stderr.
        Currently supports Python only.
        """
        if language != "python":
            return "", f"Running {language} code is not supported yet"

        try:
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return "", "Code execution timed out (30s limit)"
        except Exception as e:
            return "", str(e)

    def code_review(self, code: str, language: str = "python") -> str:
        """Perform a code review."""
        prompt = f"""Perform a thorough code review of the following {language} code:

```{language}
{code}
```

Review checklist:
- [ ] Code correctness
- [ ] Error handling
- [ ] Security considerations
- [ ] Performance
- [ ] Readability and maintainability
- [ ] Documentation
- [ ] Testing considerations

Provide specific, actionable feedback."""

        return self.ask(prompt, include_workspace=False)


def main():
    """Interactive coding assistant demo."""
    assistant = CodingAssistant()

    print("=" * 60)
    print("MiniMax-M2 Coding Assistant")
    print("=" * 60)
    print("\nCommands:")
    print("  /load <path>    - Load a file into workspace")
    print("  /analyze        - Analyze loaded code")
    print("  /write <desc>   - Generate code from description")
    print("  /fix            - Fix code with error")
    print("  /refactor       - Refactor loaded code")
    print("  /explain        - Explain loaded code")
    print("  /review         - Code review")
    print("  /run            - Run Python code")
    print("  /clear          - Clear conversation")
    print("  /quit           - Exit")
    print("\nOr just type your coding question!\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if command == "/quit":
                break
            elif command == "/clear":
                assistant.reset()
                print("Conversation cleared.")
            elif command == "/load":
                if arg:
                    code_file = assistant.load_file(arg)
                    if code_file:
                        print(f"Loaded: {code_file.path} ({code_file.language})")
                else:
                    print("Usage: /load <path>")
            elif command == "/analyze":
                if assistant.workspace_files:
                    for path, cf in assistant.workspace_files.items():
                        print(f"\n--- Analyzing {path} ---")
                        response = assistant.analyze_code(cf.content, cf.language)
                        print(f"\n{response}")
                else:
                    print("No files loaded. Use /load first.")
            elif command == "/write":
                if arg:
                    response = assistant.write_code(arg)
                    print(f"\n{response}")
                else:
                    print("Usage: /write <description>")
            elif command == "/review":
                if assistant.workspace_files:
                    for path, cf in assistant.workspace_files.items():
                        print(f"\n--- Reviewing {path} ---")
                        response = assistant.code_review(cf.content, cf.language)
                        print(f"\n{response}")
                else:
                    print("No files loaded. Use /load first.")
            elif command == "/explain":
                if assistant.workspace_files:
                    for path, cf in assistant.workspace_files.items():
                        print(f"\n--- Explaining {path} ---")
                        response = assistant.explain_code(cf.content, cf.language)
                        print(f"\n{response}")
                else:
                    print("No files loaded. Use /load first.")
            else:
                print(f"Unknown command: {command}")
        else:
            # Regular conversation
            response = assistant.ask(user_input)
            print(f"\nAssistant: {response}\n")

    print("\nGoodbye!")


if __name__ == "__main__":
    main()
