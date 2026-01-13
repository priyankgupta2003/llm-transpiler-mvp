#!/usr/bin/env python3
"""CLI script to run the single-file transpilation workflow."""

import os
import sys
import argparse
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from langgraph.graph import END
from langchain_openai import ChatOpenAI

from core import (
    State,
    StateError,
    GraphBuilder,
    SummaryAgent,
    PlanningAgent,
    TranspileAgent,
    python_format,
)
from prompts import Prompts


def compile_condition(state: State, max_iter: int) -> str:
    """Decides whether to continue transpilation on compile error or terminate.
    
    Args:
        state: Current workflow state
        max_iter: Maximum allowed iterations
        
    Returns:
        'continue' to retry, 'terminate' to end workflow
    """
    if state["last_error"].status != 0 and state["current_iterations"] < max_iter:
        return "continue"
    return "terminate"


def save_to_disk(code: str, target_path: str) -> None:
    """Save transpiled code to disk.
    
    Args:
        code: Python code to save
        target_path: Destination file path
    """
    output_path = Path(target_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        f.write(code)
    
    logger.success(f"Saved transpiled code to: {output_path}")


def main():
    """Main entry point for the transpilation CLI."""
    # Load environment variables
    load_dotenv()
    
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="AI-powered Java to Python transpiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python run_transpile.py --model-name gpt-4 --source Calculator.java --target calculator.py
  python run_transpile.py --model-name deepseek/deepseek-r1-0528:free --source examples/HelloWorld.java --target output/hello_world.py --max-iter 5
        """
    )
    parser.add_argument("--model-name", required=True, help="LLM model name")
    parser.add_argument("--source", required=True, help="Path to Java source file")
    parser.add_argument("--target", required=True, help="Path to Python output file")
    parser.add_argument(
        "--max-iter",
        type=int,
        default=3,
        help="Maximum transpilation iterations on error (default: 3)",
    )
    args = parser.parse_args()
    
    # Validate environment variables
    api_key = os.getenv("OPEN_API_KEY")
    if not api_key:
        logger.error("OPEN_API_KEY not found in environment. Please set it in .env file")
        sys.exit(1)
    
    base_url = os.getenv("OPEN_BASE_URL", "https://api.openai.com/v1")
    
    logger.info(f"Using model: {args.model_name}")
    logger.info(f"API endpoint: {base_url}")
    
    # Initialize prompts
    prompts = Prompts()
    
    # Initialize LLM client
    model = ChatOpenAI(
        model=args.model_name,
        temperature=0.2,
        api_key=api_key,
        base_url=base_url,
    )
    
    # Read source code
    source_path = Path(args.source)
    if not source_path.exists():
        logger.error(f"Source file not found: {source_path}")
        sys.exit(1)
    
    with open(source_path, "r") as sf:
        source_code = sf.read()
    
    logger.info(f"Read {len(source_code)} chars from {source_path}")
    
    # Create initial State
    state: State = {
        "code": "",
        "original_code": source_code,
        "summary": "",
        "plan": "",
        "scratchpad": "",
        "last_error": StateError(status=0, message=""),
        "current_iterations": 0,
    }
    
    # Instantiate agents with prompts
    summary_agent = SummaryAgent(
        model=model,
        system_prompt=prompts.SUMMARY_AGENT_SYSTEM_PROMPT,
        summary_user_prompt=prompts.SUMMARY_AGENT_USER_PROMPT,
    )
    
    planning_agent = PlanningAgent(
        model=model,
        system_prompt=prompts.PLANNING_AGENT_SYSTEM_PROMPT,
        planning_user_prompt=prompts.PLANNING_AGENT_USER_PROMPT,
    )
    
    transpile_agent = TranspileAgent(
        model=model,
        system_prompt=prompts.TRANSPILE_AGENT_SYSTEM_PROMPT,
        transpile_user_prompt=prompts.TRANSPILE_AGENT_USER_PROMPT,
        error_prompts={
            1: prompts.TRANSPILE_AGENT_COMPILE_ERROR_PROMPT,
        },
    )
    
    # Build the graph
    logger.info("Building transpilation workflow graph...")
    gb = GraphBuilder()
    gb.add_node(summary_agent)
    gb.add_node(planning_agent)
    gb.add_node(transpile_agent)
    
    # Define workflow edges
    gb.set_entry_point(summary_agent)
    gb.add_edge(summary_agent, planning_agent)
    gb.add_edge(planning_agent, transpile_agent)
    gb.add_conditional_edge(
        transpile_agent,
        lambda s: compile_condition(s, args.max_iter),
        {"continue": transpile_agent.name, "terminate": END},
    )
    
    # Compile and run the state graph
    logger.info("Starting transpilation workflow...")
    graph = gb.compile()
    final_state = graph.invoke(state)
    
    # Check if transpilation was successful
    if final_state["last_error"].status != 0:
        logger.error("Transpilation failed after maximum retries")
        logger.error(f"Last error: {final_state['last_error'].message}")
        sys.exit(1)
    
    # Post-processing with tools
    logger.info("Formatting code with Black...")
    final_state["code"] = python_format(final_state["code"])
    
    # Save to disk
    save_to_disk(final_state["code"], args.target)
    
    logger.success("✨ Transpilation completed successfully!")


if __name__ == "__main__":
    main()