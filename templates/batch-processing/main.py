"""
MiniMax-M2 Batch Processing Template
====================================
A template for processing multiple prompts efficiently with MiniMax-M2.

Features:
- Concurrent request handling
- Progress tracking
- Error handling and retries
- Result aggregation
- CSV/JSON export

Requirements:
    pip install openai tqdm

Usage:
    python main.py
"""

import json
import csv
import time
import asyncio
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Configuration
API_BASE_URL = "http://localhost:8000/v1"
API_KEY = "your-api-key-here"
MODEL_NAME = "MiniMax-M2"


@dataclass
class BatchRequest:
    """A single request in a batch."""
    id: str
    prompt: str
    system_prompt: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class BatchResult:
    """Result of a batch request."""
    id: str
    prompt: str
    response: str
    success: bool
    error: Optional[str] = None
    latency_ms: float = 0
    tokens_used: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    max_concurrent: int = 5
    max_retries: int = 3
    retry_delay: float = 1.0
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: float = 60.0


class BatchProcessor:
    """Process multiple prompts efficiently."""

    def __init__(
        self,
        api_key: str = API_KEY,
        base_url: str = API_BASE_URL,
        config: Optional[BatchConfig] = None
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.config = config or BatchConfig()
        self.results: list[BatchResult] = []

    def _process_single(self, request: BatchRequest) -> BatchResult:
        """Process a single request with retries."""
        start_time = time.time()
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                messages = []

                # Add system prompt if provided
                system = request.system_prompt or "You are a helpful AI assistant."
                messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": request.prompt})

                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    timeout=self.config.timeout,
                )

                latency = (time.time() - start_time) * 1000
                tokens = response.usage.total_tokens if response.usage else 0

                return BatchResult(
                    id=request.id,
                    prompt=request.prompt,
                    response=response.choices[0].message.content,
                    success=True,
                    latency_ms=latency,
                    tokens_used=tokens,
                    metadata=request.metadata,
                )

            except Exception as e:
                last_error = str(e)
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))

        # All retries failed
        latency = (time.time() - start_time) * 1000
        return BatchResult(
            id=request.id,
            prompt=request.prompt,
            response="",
            success=False,
            error=last_error,
            latency_ms=latency,
            metadata=request.metadata,
        )

    def process(self, requests: list[BatchRequest]) -> list[BatchResult]:
        """
        Process a batch of requests concurrently.

        Args:
            requests: List of batch requests to process

        Returns:
            List of batch results
        """
        self.results = []

        if TQDM_AVAILABLE:
            progress = tqdm(total=len(requests), desc="Processing")
        else:
            progress = None
            print(f"Processing {len(requests)} requests...")

        with ThreadPoolExecutor(max_workers=self.config.max_concurrent) as executor:
            futures = {
                executor.submit(self._process_single, req): req
                for req in requests
            }

            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)

                if progress:
                    progress.update(1)
                else:
                    status = "OK" if result.success else "FAIL"
                    print(f"  [{status}] {result.id}")

        if progress:
            progress.close()

        return self.results

    def process_from_file(self, filepath: str) -> list[BatchResult]:
        """
        Process requests from a JSON file.

        Expected format:
        [
            {"id": "1", "prompt": "...", "system_prompt": "...", "metadata": {}},
            ...
        ]
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        requests = [
            BatchRequest(
                id=item.get("id", str(i)),
                prompt=item["prompt"],
                system_prompt=item.get("system_prompt"),
                metadata=item.get("metadata", {}),
            )
            for i, item in enumerate(data)
        ]

        return self.process(requests)

    def save_results(self, filepath: str, format: str = "json"):
        """
        Save results to a file.

        Args:
            filepath: Output file path
            format: 'json' or 'csv'
        """
        if format == "json":
            self._save_json(filepath)
        elif format == "csv":
            self._save_csv(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _save_json(self, filepath: str):
        """Save results as JSON."""
        with open(filepath, 'w') as f:
            json.dump([asdict(r) for r in self.results], f, indent=2)
        print(f"Results saved to: {filepath}")

    def _save_csv(self, filepath: str):
        """Save results as CSV."""
        if not self.results:
            return

        fieldnames = ['id', 'prompt', 'response', 'success', 'error', 'latency_ms', 'tokens_used']

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                row = {k: getattr(result, k) for k in fieldnames}
                writer.writerow(row)

        print(f"Results saved to: {filepath}")

    def get_statistics(self) -> dict:
        """Get statistics about the batch processing."""
        if not self.results:
            return {}

        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        latencies = [r.latency_ms for r in successful]
        tokens = [r.tokens_used for r in successful]

        return {
            "total_requests": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(self.results) * 100,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "total_tokens": sum(tokens),
            "avg_tokens": sum(tokens) / len(tokens) if tokens else 0,
        }

    def print_statistics(self):
        """Print batch processing statistics."""
        stats = self.get_statistics()

        if not stats:
            print("No results to analyze.")
            return

        print("\n" + "=" * 50)
        print("Batch Processing Statistics")
        print("=" * 50)
        print(f"Total Requests:    {stats['total_requests']}")
        print(f"Successful:        {stats['successful']}")
        print(f"Failed:            {stats['failed']}")
        print(f"Success Rate:      {stats['success_rate']:.1f}%")
        print(f"Average Latency:   {stats['avg_latency_ms']:.0f}ms")
        print(f"Min Latency:       {stats['min_latency_ms']:.0f}ms")
        print(f"Max Latency:       {stats['max_latency_ms']:.0f}ms")
        print(f"Total Tokens:      {stats['total_tokens']}")
        print(f"Average Tokens:    {stats['avg_tokens']:.0f}")
        print("=" * 50)


def create_sample_requests() -> list[BatchRequest]:
    """Create sample batch requests for demonstration."""
    prompts = [
        "What is the capital of France?",
        "Explain quantum computing in one sentence.",
        "Write a haiku about programming.",
        "What is 2 + 2?",
        "Name three programming languages.",
        "What is machine learning?",
        "Explain recursion simply.",
        "What is an API?",
        "Define 'algorithm'.",
        "What is the speed of light?",
    ]

    return [
        BatchRequest(
            id=f"req_{i}",
            prompt=prompt,
            metadata={"category": "general"}
        )
        for i, prompt in enumerate(prompts)
    ]


def main():
    """Demonstrate batch processing."""
    print("=" * 60)
    print("MiniMax-M2 Batch Processing Demo")
    print("=" * 60)

    # Configure batch processing
    config = BatchConfig(
        max_concurrent=3,
        max_retries=2,
        temperature=0.5,
        max_tokens=256,
    )

    processor = BatchProcessor(config=config)

    # Create sample requests
    requests = create_sample_requests()
    print(f"\nProcessing {len(requests)} requests...")
    print(f"Concurrency: {config.max_concurrent}")
    print()

    # Process batch
    results = processor.process(requests)

    # Print statistics
    processor.print_statistics()

    # Show sample results
    print("\nSample Results:")
    print("-" * 50)
    for result in results[:3]:
        status = "OK" if result.success else "FAIL"
        print(f"\n[{status}] {result.id}")
        print(f"Q: {result.prompt}")
        if result.success:
            print(f"A: {result.response[:200]}...")
        else:
            print(f"Error: {result.error}")

    # Save results
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    processor.save_results(str(output_dir / "results.json"), format="json")
    processor.save_results(str(output_dir / "results.csv"), format="csv")


if __name__ == "__main__":
    main()
