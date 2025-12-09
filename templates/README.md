# MiniMax-M2 Project Templates

Ready-to-use project templates to quickly get started with MiniMax-M2.

## Available Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| [basic-api](./basic-api) | Simple API interaction | Getting started, basic queries |
| [tool-calling-agent](./tool-calling-agent) | Agent with function calling | Agentic workflows, automation |
| [coding-assistant](./coding-assistant) | Code analysis and generation | Development assistance |
| [streaming-chat](./streaming-chat) | Real-time chat interface | Interactive applications |
| [batch-processing](./batch-processing) | Process multiple prompts | Data processing, evaluation |

## Quick Start

1. Choose a template that fits your use case
2. Copy the template directory to your project
3. Install dependencies: `pip install -r requirements.txt`
4. Configure your API key and endpoint
5. Run: `python main.py`

## Template Structure

Each template follows a consistent structure:

```
template-name/
├── main.py           # Main application code
├── requirements.txt  # Python dependencies
├── README.md         # Template documentation
└── .env.example      # Environment configuration (if applicable)
```

## Configuration

All templates use these common environment variables:

```bash
API_BASE_URL=http://localhost:8000/v1  # For local deployment
API_KEY=your-api-key-here
MODEL_NAME=MiniMax-M2
```

### Local Deployment
Use with SGLang or vLLM deployment:
```bash
API_BASE_URL=http://localhost:8000/v1
```

### Cloud API
Use MiniMax cloud service:
```bash
API_BASE_URL=https://api.minimax.chat/v1
```

## Template Descriptions

### Basic API
The simplest template for getting started. Demonstrates:
- Creating an API client
- Simple completions
- Streaming responses

### Tool-Calling Agent
Build AI agents that can use tools. Features:
- Tool/function definitions
- Automatic tool execution
- Multi-turn conversations
- Extensible tool registry

### Coding Assistant
A powerful coding helper. Capabilities:
- Code analysis and review
- Code generation
- Bug fixing
- Refactoring suggestions
- Multi-language support

### Streaming Chat
Real-time chat application. Features:
- Token-by-token streaming
- Multiple conversations
- Thinking mode toggle
- Rich terminal display

### Batch Processing
Process many requests efficiently. Features:
- Concurrent execution
- Automatic retries
- Progress tracking
- JSON/CSV export
- Statistics reporting

## Requirements

- Python 3.9+
- OpenAI SDK (`pip install openai`)
- Template-specific dependencies (see individual requirements.txt)

## MiniMax-M2 Highlights

These templates leverage MiniMax-M2's strengths:

- **Coding Excellence**: #1 on SWE-bench (69.4%) and LiveCodeBench (83%)
- **Agentic Workflows**: Complex tool use with graceful error recovery
- **Efficiency**: Only 10B active parameters for fast inference
- **Thinking Mode**: Extended reasoning with `<think>` tags

## Contributing

To add a new template:

1. Create a new directory under `templates/`
2. Include `main.py`, `requirements.txt`, and `README.md`
3. Follow the existing template patterns
4. Submit a pull request

## Resources

- [MiniMax-M2 Documentation](../README.md)
- [Tool Calling Guide](../docs/tool_calling_guide.md)
- [Deployment Guides](../docs/)
- [MiniMax Platform](https://platform.minimax.io/)
