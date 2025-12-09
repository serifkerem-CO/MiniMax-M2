# MiniMax-M2 Basic API Template

A simple template demonstrating how to interact with the MiniMax-M2 model using the OpenAI-compatible API.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your environment:
```bash
cp .env.example .env
# Edit .env with your API key and endpoint
```

3. Run the example:
```bash
python main.py
```

## Features

- Simple completion requests
- Streaming responses
- Environment-based configuration

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | API endpoint URL | `http://localhost:8000/v1` |
| `API_KEY` | Your API key | - |
| `MODEL_NAME` | Model identifier | `MiniMax-M2` |

## Usage Examples

### Simple Completion
```python
from main import create_client, simple_completion

client = create_client()
response = simple_completion(client, "Write a hello world in Python")
print(response)
```

### Streaming
```python
from main import create_client, streaming_completion

client = create_client()
for chunk in streaming_completion(client, "Explain recursion"):
    print(chunk, end="")
```
