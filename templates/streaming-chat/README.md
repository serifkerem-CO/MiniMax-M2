# MiniMax-M2 Streaming Chat Template

A real-time streaming chat application template using MiniMax-M2.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your API settings in `main.py`

3. Run:
```bash
python main.py
```

## Features

- **Real-time Streaming**: See responses as they generate
- **Multi-conversation**: Manage multiple chat sessions
- **Thinking Toggle**: Show/hide model's thinking process
- **Graceful Interruption**: Press Ctrl+C to stop generation
- **Rich Display**: Beautiful markdown rendering (with rich library)

## Commands

| Command | Description |
|---------|-------------|
| `/new [name]` | Start new conversation |
| `/switch <name>` | Switch to conversation |
| `/list` | List all conversations |
| `/clear` | Clear current conversation |
| `/thinking` | Toggle thinking display |
| `/temp <0-1>` | Set temperature |
| `/quit` | Exit |

## Usage Patterns

### Basic Streaming
```python
from main import StreamingChat

chat = StreamingChat()

for chunk in chat.stream_response("Hello!"):
    print(chunk, end="", flush=True)
```

### With Display
```python
chat = StreamingChat()
response = chat.chat_with_display("Explain quantum computing")
```

### Conversation Management
```python
from main import ConversationManager, ChatConfig

manager = ConversationManager()

# Create conversations with different configs
manager.create("creative", ChatConfig(temperature=0.9))
manager.create("precise", ChatConfig(temperature=0.1))

# Switch between them
creative_chat = manager.switch("creative")
precise_chat = manager.switch("precise")
```

## Configuration

```python
config = ChatConfig(
    temperature=0.7,      # Creativity (0-1)
    max_tokens=4096,      # Response length limit
    show_thinking=False,  # Display <think> tags
    system_prompt="..."   # Custom system prompt
)
```

## Thinking Mode

MiniMax-M2 uses `<think>...</think>` tags for internal reasoning. By default, these are hidden. Use `/thinking` to toggle visibility.
