# MiniMax-M2 Batch Processing Template

A template for efficiently processing multiple prompts with MiniMax-M2.

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

- **Concurrent Processing**: Handle multiple requests in parallel
- **Automatic Retries**: Recover from transient failures
- **Progress Tracking**: Visual progress bar with tqdm
- **Statistics**: Latency, token usage, success rates
- **Export**: Save results to JSON or CSV

## Configuration

```python
config = BatchConfig(
    max_concurrent=5,     # Parallel requests
    max_retries=3,        # Retry attempts
    retry_delay=1.0,      # Seconds between retries
    temperature=0.7,      # Model temperature
    max_tokens=2048,      # Max response tokens
    timeout=60.0,         # Request timeout
)
```

## Usage

### From Code
```python
from main import BatchProcessor, BatchRequest, BatchConfig

# Create processor
processor = BatchProcessor(config=BatchConfig(max_concurrent=5))

# Create requests
requests = [
    BatchRequest(id="1", prompt="What is AI?"),
    BatchRequest(id="2", prompt="Explain ML"),
    BatchRequest(id="3", prompt="Define NLP"),
]

# Process
results = processor.process(requests)

# Get statistics
processor.print_statistics()

# Save results
processor.save_results("output.json")
```

### From File
```python
# requests.json:
# [
#   {"id": "1", "prompt": "Question 1"},
#   {"id": "2", "prompt": "Question 2"}
# ]

processor = BatchProcessor()
results = processor.process_from_file("requests.json")
```

## Input File Format

JSON array of request objects:

```json
[
  {
    "id": "unique_id",
    "prompt": "Your prompt here",
    "system_prompt": "Optional system prompt",
    "metadata": {"any": "extra data"}
  }
]
```

## Output Format

### JSON
```json
[
  {
    "id": "1",
    "prompt": "What is AI?",
    "response": "AI is...",
    "success": true,
    "error": null,
    "latency_ms": 1234.5,
    "tokens_used": 150,
    "metadata": {}
  }
]
```

### CSV
```
id,prompt,response,success,error,latency_ms,tokens_used
1,What is AI?,AI is...,True,,1234.5,150
```

## Use Cases

- **Data Processing**: Classify, summarize, or transform datasets
- **Content Generation**: Generate multiple variations
- **Testing**: Evaluate model responses at scale
- **Evaluation**: Benchmark prompts across different parameters
