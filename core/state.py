"""State management for the transpilation workflow."""

from dataclasses import dataclass, field
from typing import TypedDict


@dataclass
class StateError:
    """Represents a compilation or runtime error."""
    status: int  # 0 = no error, 1 = compile error, 2 = output mismatch
    message: str  # Error message or stack trace


class State(TypedDict, total=False):
    """State maintained throughout the transpilation workflow.
    
    Attributes:
        code: Current transpiled Python code
        original_code: Input Java source code
        summary: Technical summary of Java code
        plan: Step-by-step migration plan
        scratchpad: Working notes for agents
        last_error: Most recent error details
        current_iterations: Number of retry attempts
    """
    code: str
    original_code: str
    summary: str
    plan: str
    scratchpad: str
    last_error: StateError
    current_iterations: int