"""
MiniMax-M2 Basic API Usage Template
===================================
A simple template demonstrating how to interact with MiniMax-M2 model
using the OpenAI-compatible API.

Requirements:
    pip install openai

Usage:
    python main.py
"""

from openai import OpenAI

# Configuration
API_BASE_URL = "http://localhost:8000/v1"  # Local deployment
# API_BASE_URL = "https://api.minimax.chat/v1"  # Cloud API
API_KEY = "your-api-key-here"  # Replace with your actual API key
MODEL_NAME = "MiniMax-M2"


def create_client() -> OpenAI:
    """Create and return an OpenAI-compatible client."""
    return OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL,
    )


def simple_completion(client: OpenAI, prompt: str) -> str:
    """
    Send a simple completion request to MiniMax-M2.

    Args:
        client: OpenAI client instance
        prompt: User prompt to send

    Returns:
        Model response as string
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant powered by MiniMax-M2."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=2048,
    )

    return response.choices[0].message.content


def streaming_completion(client: OpenAI, prompt: str):
    """
    Send a streaming completion request to MiniMax-M2.

    Args:
        client: OpenAI client instance
        prompt: User prompt to send

    Yields:
        Response chunks as they arrive
    """
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant powered by MiniMax-M2."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=2048,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def main():
    """Main entry point demonstrating basic API usage."""
    client = create_client()

    # Example 1: Simple completion
    print("=" * 50)
    print("Example 1: Simple Completion")
    print("=" * 50)

    prompt = "Write a Python function to calculate the Fibonacci sequence."
    response = simple_completion(client, prompt)
    print(f"Prompt: {prompt}\n")
    print(f"Response:\n{response}\n")

    # Example 2: Streaming completion
    print("=" * 50)
    print("Example 2: Streaming Completion")
    print("=" * 50)

    prompt = "Explain the concept of Mixture of Experts (MoE) in AI models."
    print(f"Prompt: {prompt}\n")
    print("Response (streaming):")

    for chunk in streaming_completion(client, prompt):
        print(chunk, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    main()
