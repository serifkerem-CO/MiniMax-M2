"""
MiniMax-M2 Streaming Chat Template
==================================
A template for building real-time streaming chat applications with MiniMax-M2.

Features:
- Real-time token streaming
- Conversation history management
- Thinking tag handling
- Graceful interruption

Requirements:
    pip install openai rich

Usage:
    python main.py
"""

import sys
import signal
from typing import Generator, Optional
from dataclasses import dataclass, field
from openai import OpenAI

try:
    from rich.console import Console
    from rich.live import Live
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Configuration
API_BASE_URL = "http://localhost:8000/v1"
API_KEY = "your-api-key-here"
MODEL_NAME = "MiniMax-M2"


@dataclass
class Message:
    """Represents a chat message."""
    role: str  # 'user', 'assistant', 'system'
    content: str


@dataclass
class ChatConfig:
    """Configuration for chat behavior."""
    temperature: float = 0.7
    max_tokens: int = 4096
    show_thinking: bool = False  # Whether to display <think> tags
    system_prompt: str = "You are a helpful AI assistant powered by MiniMax-M2."


class StreamingChat:
    """A streaming chat interface for MiniMax-M2."""

    def __init__(
        self,
        api_key: str = API_KEY,
        base_url: str = API_BASE_URL,
        config: Optional[ChatConfig] = None
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.config = config or ChatConfig()
        self.messages: list[Message] = []
        self.console = Console() if RICH_AVAILABLE else None
        self._interrupted = False

        # Set up signal handler for graceful interruption
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _handle_interrupt(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        self._interrupted = True

    def reset(self):
        """Reset conversation history."""
        self.messages = []
        self._interrupted = False

    def _format_messages(self) -> list[dict]:
        """Format messages for API call."""
        formatted = [
            {"role": "system", "content": self.config.system_prompt}
        ]
        for msg in self.messages:
            formatted.append({"role": msg.role, "content": msg.content})
        return formatted

    def _filter_thinking(self, text: str) -> str:
        """Remove <think>...</think> tags if not showing thinking."""
        if self.config.show_thinking:
            return text

        import re
        # Remove thinking tags and their content
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    def stream_response(self, user_message: str) -> Generator[str, None, str]:
        """
        Stream a response for the given user message.

        Args:
            user_message: The user's input

        Yields:
            Response chunks as they arrive

        Returns:
            Complete response text
        """
        self._interrupted = False

        # Add user message to history
        self.messages.append(Message(role="user", content=user_message))

        # Create streaming request
        stream = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=self._format_messages(),
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
        )

        full_response = ""
        in_thinking = False
        thinking_buffer = ""

        for chunk in stream:
            if self._interrupted:
                full_response += "\n[Interrupted]"
                break

            delta = chunk.choices[0].delta
            if delta.content:
                content = delta.content
                full_response += content

                # Handle thinking tags
                if not self.config.show_thinking:
                    # Track if we're inside thinking tags
                    if "<think>" in content:
                        in_thinking = True
                        thinking_buffer = content.split("<think>")[0]
                        if thinking_buffer:
                            yield thinking_buffer
                        continue
                    elif "</think>" in content:
                        in_thinking = False
                        after_think = content.split("</think>")[-1]
                        if after_think:
                            yield after_think
                        continue
                    elif in_thinking:
                        continue

                yield content

        # Add assistant response to history
        filtered_response = self._filter_thinking(full_response)
        self.messages.append(Message(role="assistant", content=filtered_response))

        return full_response

    def chat(self, user_message: str) -> str:
        """
        Send a message and get the complete response.

        Args:
            user_message: The user's input

        Returns:
            Complete response text
        """
        response_parts = []
        for chunk in self.stream_response(user_message):
            response_parts.append(chunk)
        return "".join(response_parts)

    def chat_with_display(self, user_message: str) -> str:
        """
        Send a message and display streaming response in terminal.

        Args:
            user_message: The user's input

        Returns:
            Complete response text
        """
        if self.console and RICH_AVAILABLE:
            return self._chat_with_rich(user_message)
        else:
            return self._chat_simple(user_message)

    def _chat_with_rich(self, user_message: str) -> str:
        """Chat with rich terminal display."""
        response_text = ""

        with Live(console=self.console, refresh_per_second=10) as live:
            for chunk in self.stream_response(user_message):
                response_text += chunk
                live.update(Markdown(response_text))

        return response_text

    def _chat_simple(self, user_message: str) -> str:
        """Chat with simple terminal display."""
        response_text = ""

        for chunk in self.stream_response(user_message):
            print(chunk, end="", flush=True)
            response_text += chunk

        print()  # New line after response
        return response_text


class ConversationManager:
    """Manages multiple conversations."""

    def __init__(self):
        self.conversations: dict[str, StreamingChat] = {}
        self.current_id: Optional[str] = None

    def create(self, conversation_id: str, config: Optional[ChatConfig] = None) -> StreamingChat:
        """Create a new conversation."""
        chat = StreamingChat(config=config)
        self.conversations[conversation_id] = chat
        self.current_id = conversation_id
        return chat

    def get(self, conversation_id: str) -> Optional[StreamingChat]:
        """Get an existing conversation."""
        return self.conversations.get(conversation_id)

    def switch(self, conversation_id: str) -> Optional[StreamingChat]:
        """Switch to a different conversation."""
        if conversation_id in self.conversations:
            self.current_id = conversation_id
            return self.conversations[conversation_id]
        return None

    def current(self) -> Optional[StreamingChat]:
        """Get current conversation."""
        if self.current_id:
            return self.conversations.get(self.current_id)
        return None

    def list_conversations(self) -> list[str]:
        """List all conversation IDs."""
        return list(self.conversations.keys())

    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            if self.current_id == conversation_id:
                self.current_id = None
            return True
        return False


def interactive_mode():
    """Run interactive chat mode."""
    print("=" * 60)
    print("MiniMax-M2 Streaming Chat")
    print("=" * 60)
    print("\nCommands:")
    print("  /new [name]     - Start new conversation")
    print("  /switch <name>  - Switch conversation")
    print("  /list           - List conversations")
    print("  /clear          - Clear current conversation")
    print("  /thinking       - Toggle thinking display")
    print("  /temp <value>   - Set temperature (0-1)")
    print("  /quit           - Exit")
    print("\nPress Ctrl+C to interrupt streaming.\n")

    manager = ConversationManager()
    config = ChatConfig()

    # Create default conversation
    chat = manager.create("default", config)
    print("Started conversation: default\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if command == "/quit":
                print("Goodbye!")
                break
            elif command == "/new":
                name = arg or f"conv_{len(manager.conversations)}"
                chat = manager.create(name, config)
                print(f"Created new conversation: {name}")
            elif command == "/switch":
                if arg:
                    switched = manager.switch(arg)
                    if switched:
                        chat = switched
                        print(f"Switched to: {arg}")
                    else:
                        print(f"Conversation not found: {arg}")
                else:
                    print("Usage: /switch <name>")
            elif command == "/list":
                convs = manager.list_conversations()
                current = manager.current_id
                for c in convs:
                    marker = " *" if c == current else ""
                    print(f"  - {c}{marker}")
            elif command == "/clear":
                chat.reset()
                print("Conversation cleared.")
            elif command == "/thinking":
                config.show_thinking = not config.show_thinking
                chat.config.show_thinking = config.show_thinking
                status = "ON" if config.show_thinking else "OFF"
                print(f"Thinking display: {status}")
            elif command == "/temp":
                try:
                    temp = float(arg)
                    if 0 <= temp <= 1:
                        config.temperature = temp
                        chat.config.temperature = temp
                        print(f"Temperature set to: {temp}")
                    else:
                        print("Temperature must be between 0 and 1")
                except ValueError:
                    print("Usage: /temp <0-1>")
            else:
                print(f"Unknown command: {command}")
        else:
            print("\nAssistant: ", end="")
            chat.chat_with_display(user_input)
            print()


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Demo mode: single question
        chat = StreamingChat()
        print("Demo: Asking about Python...")
        print("\nAssistant: ", end="")
        chat.chat_with_display("What are the key features of Python 3.12?")
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
