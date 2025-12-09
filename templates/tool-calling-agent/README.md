# MiniMax-M2 Tool-Calling Agent Template

A template for building AI agents with tool/function calling capabilities using MiniMax-M2.

MiniMax-M2 excels at agentic workflows with complex, long-horizon tool use, graceful error recovery, and evidence-traced retrieval.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your API settings in `main.py`

3. Run the example:
```bash
python main.py
```

## Features

- Tool/function calling with automatic execution
- Multi-turn conversation support
- Extensible tool registry
- Interactive mode

## Available Tools

| Tool | Description |
|------|-------------|
| `get_weather` | Get weather for a location |
| `search_web` | Search the web |
| `execute_code` | Execute Python code |
| `read_file` | Read file contents |
| `write_file` | Write to a file |

## Adding Custom Tools

1. Define the tool schema in `TOOLS` list:
```python
{
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "What the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."}
            },
            "required": ["param1"]
        }
    }
}
```

2. Implement the function:
```python
def my_tool(param1: str) -> dict:
    # Your implementation
    return {"result": "..."}
```

3. Register in `TOOL_FUNCTIONS`:
```python
TOOL_FUNCTIONS["my_tool"] = my_tool
```

## Tool Calling Format

MiniMax-M2 uses an XML-based internal format for tool calls:

```xml
<tool_call>
{"name": "tool_name", "arguments": {"key": "value"}}
</tool_call>
```

The OpenAI SDK handles parsing automatically when using the `tools` parameter.

## Best Practices

1. **Clear Tool Descriptions**: Write detailed descriptions for each tool
2. **Error Handling**: Tools should return structured error responses
3. **Iteration Limits**: Set reasonable `max_iterations` to prevent infinite loops
4. **Sandboxing**: Use proper sandboxing for code execution tools
