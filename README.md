# LLM Transpiler MVP

An AI-powered code transpiler that converts Java code to Python using LLMs with structured multi-step reasoning.

## What is this?

Instead of naive line-by-line translation, this transpiler uses an intelligent workflow:
1. **Summarize** - Understand the Java code structure and purpose
2. **Plan** - Generate a detailed step-by-step transpilation strategy
3. **Transpile** - Convert Java to Python based on the plan
4. **Fix Loop** - Iteratively fix compilation errors until code works
5. **Format** - Apply Black formatter for PEP8 compliance

## Key Insight

Code transpilation is a **planning + iterative refinement problem**, not a direct translation problem. By having the LLM understand the code first, plan the migration, and fix errors in a loop, you get dramatically better results than simple AST transforms.

## Features

✅ Single-file Java → Python transpilation
✅ LangGraph-based state machine workflow
✅ Automatic compilation error detection and fixing
✅ PEP8 formatting with Black
✅ Works with any OpenAI-compatible LLM endpoint
✅ Configurable retry limits

## Installation

### Prerequisites
- Python 3.12 or higher
- pip or uv package manager

### Install dependencies

```bash
pip install -e .
```

Or with uv:

```bash
uv pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Edit `.env` and add your API credentials:

```env
OPEN_API_KEY="your-api-key-here"
OPEN_BASE_URL="https://openrouter.ai/api/v1"  # or any OpenAI-compatible endpoint
```

## Usage

### Basic Usage

```bash
python run_transpile.py --model-name deepseek/deepseek-r1-0528:free --source examples/HelloWorld.java --target output/hello_world.py
```

### Command-line Arguments

- `--model-name` (required): LLM model name (e.g., `gpt-4`, `deepseek/deepseek-r1-0528:free`)
- `--source` (required): Path to Java source file
- `--target` (required): Path where Python output should be saved
- `--max-iter` (optional): Maximum transpilation retry attempts on errors (default: 3)

### Example

```bash
# Transpile a Java calculator class
python run_transpile.py \
  --model-name gpt-4 \
  --source examples/Calculator.java \
  --target output/calculator.py \
  --max-iter 5
```

## How It Works

### LangGraph Workflow

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Summary Agent   │  ← Analyzes Java code structure
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Planning Agent  │  ← Creates step-by-step plan
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transpile Agent │  ← Generates Python code
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │Compile?│
    └───┬─┬──┘
        │ │
    ✅  │ │  ❌ (error)
        │ └──────┐
        │        │
        ▼        ▼
  ┌─────────┐  ┌──────────────┐
  │ Format  │  │ Retry < max? │
  │ (Black) │  └──────┬───────┘
  └────┬────┘         │
       │         Yes  │  No
       │         ┌────┴────┐
       │         │ Loop    │  FAIL
       │         │ back    │
       │         └─────────┘
       ▼
   ┌──────┐
   │ DONE │
   └──────┘
```

### State Structure

The workflow maintains state through each node:

```python
@dataclass
class State:
    original_code: str        # Input Java code
    code: str                 # Current Python code
    summary: str              # Technical summary
    plan: str                 # Migration plan
    scratchpad: str          # Working notes
    last_error: StateError   # Compilation error details
    current_iterations: int  # Retry counter
```

## Architecture

```
llm-transpiler-mvp/
├── core/
│   ├── __init__.py           # Package exports
│   ├── state.py              # State & StateError dataclasses
│   ├── graph_builder.py      # LangGraph construction utilities
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── summary_agent.py    # Code summarization
│   │   ├── planning_agent.py   # Migration planning
│   │   └── transpile_agent.py  # Code generation & fixing
│   └── tools/
│       ├── __init__.py
│       ├── compiler.py         # Python compilation check
│       └── formatter.py        # Black code formatting
├── prompts.py                # LLM system/user prompts
├── run_transpile.py          # CLI entry point
├── .env.example              # Config template
├── pyproject.toml            # Dependencies
└── README.md
```

## What's NOT in the MVP

This MVP focuses on single-file transpilation. The following features are planned for v2:

❌ Project-level transpilation (multiple files)
❌ Dependency graph analysis
❌ Parallel file processing
❌ Test generation/cloning
❌ Search agent (web search for complex questions)
❌ Project optimization pass

## Tech Stack

- **Python 3.12+**
- **LangChain 0.3.25** - LLM orchestration
- **LangGraph 0.4.5** - State machine workflow
- **OpenAI SDK 1.78.1** - LLM API communication
- **Black 25.1.0** - Python code formatting
- **Loguru 0.7.3** - Structured logging
- **python-dotenv 1.1.0** - Environment config

## Contributing

Contributions welcome! This is an MVP - there's lots of room for improvement.

## License

MIT

## Acknowledgments

Inspired by [AlphaCodium](https://www.codium.ai/products/alpha-codium/) research and built with [LangGraph](https://langchain-ai.github.io/langgraph/).