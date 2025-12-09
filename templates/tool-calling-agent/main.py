"""
MiniMax-M2 Tool-Calling Agent Template
======================================
A template demonstrating how to build an AI agent with tool/function calling
capabilities using MiniMax-M2.

MiniMax-M2 excels at agentic workflows with complex, long-horizon tool use.

Requirements:
    pip install openai

Usage:
    python main.py
"""

import json
from typing import Any, Callable
from openai import OpenAI

# Configuration
API_BASE_URL = "http://localhost:8000/v1"
API_KEY = "your-api-key-here"
MODEL_NAME = "MiniMax-M2"


# ============================================================================
# Tool Definitions
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and country, e.g. 'Tokyo, Japan'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "Execute Python code and return the result",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    }
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    }
                },
                "required": ["path", "content"]
            }
        }
    }
]


# ============================================================================
# Tool Implementations
# ============================================================================

def get_weather(location: str, unit: str = "celsius") -> dict:
    """Simulated weather API call."""
    # In production, replace with actual API call
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "condition": "sunny",
        "humidity": 45
    }


def search_web(query: str, num_results: int = 5) -> dict:
    """Simulated web search."""
    # In production, replace with actual search API
    return {
        "query": query,
        "results": [
            {"title": f"Result {i+1} for '{query}'", "url": f"https://example.com/{i}"}
            for i in range(num_results)
        ]
    }


def execute_code(code: str) -> dict:
    """Execute Python code safely."""
    try:
        # WARNING: In production, use proper sandboxing!
        local_vars = {}
        exec(code, {"__builtins__": {}}, local_vars)
        return {"status": "success", "result": str(local_vars)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def read_file(path: str) -> dict:
    """Read file contents."""
    try:
        with open(path, 'r') as f:
            return {"status": "success", "content": f.read()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def write_file(path: str, content: str) -> dict:
    """Write content to file."""
    try:
        with open(path, 'w') as f:
            f.write(content)
        return {"status": "success", "message": f"Written to {path}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Tool registry
TOOL_FUNCTIONS: dict[str, Callable] = {
    "get_weather": get_weather,
    "search_web": search_web,
    "execute_code": execute_code,
    "read_file": read_file,
    "write_file": write_file,
}


# ============================================================================
# Agent Implementation
# ============================================================================

class ToolCallingAgent:
    """An agent that can use tools to accomplish tasks."""

    def __init__(self, api_key: str = API_KEY, base_url: str = API_BASE_URL):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.messages = []
        self.system_prompt = """You are a helpful AI agent powered by MiniMax-M2.
You have access to various tools to help users accomplish their tasks.
Use tools when necessary to provide accurate and helpful responses.
Think step by step and use multiple tools if needed to complete complex tasks."""

    def reset(self):
        """Reset conversation history."""
        self.messages = []

    def execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """Execute a tool and return the result."""
        if tool_name not in TOOL_FUNCTIONS:
            return {"error": f"Unknown tool: {tool_name}"}

        func = TOOL_FUNCTIONS[tool_name]
        return func(**arguments)

    def run(self, user_message: str, max_iterations: int = 10) -> str:
        """
        Run the agent with a user message.

        Args:
            user_message: The user's input
            max_iterations: Maximum number of tool-calling iterations

        Returns:
            Final response from the agent
        """
        # Add system message if this is the start of conversation
        if not self.messages:
            self.messages.append({
                "role": "system",
                "content": self.system_prompt
            })

        # Add user message
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        for iteration in range(max_iterations):
            # Get model response
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto",
            )

            assistant_message = response.choices[0].message

            # Add assistant message to history
            self.messages.append(assistant_message.model_dump())

            # Check if we need to call tools
            if not assistant_message.tool_calls:
                # No tool calls, return the response
                return assistant_message.content

            # Process tool calls
            print(f"\n[Iteration {iteration + 1}] Executing tools...")

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                print(f"  - Calling {tool_name} with {arguments}")

                # Execute the tool
                result = self.execute_tool(tool_name, arguments)

                print(f"  - Result: {result}")

                # Add tool result to messages
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

        return "Maximum iterations reached. Task may be incomplete."


# ============================================================================
# Main
# ============================================================================

def main():
    """Demonstrate the tool-calling agent."""
    agent = ToolCallingAgent()

    print("=" * 60)
    print("MiniMax-M2 Tool-Calling Agent Demo")
    print("=" * 60)

    # Example 1: Weather query
    print("\n--- Example 1: Weather Query ---")
    response = agent.run("What's the weather like in Tokyo?")
    print(f"\nAgent Response:\n{response}")

    # Reset for next example
    agent.reset()

    # Example 2: Multi-step task
    print("\n--- Example 2: Multi-Step Task ---")
    response = agent.run(
        "Search for 'Python best practices' and then write a summary to 'summary.txt'"
    )
    print(f"\nAgent Response:\n{response}")

    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive Mode (type 'quit' to exit)")
    print("=" * 60)

    agent.reset()
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        if not user_input:
            continue

        response = agent.run(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()
