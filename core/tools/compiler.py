"""Python compilation verification tool."""

import py_compile
import tempfile
import os
from loguru import logger
from core.state import StateError


def check_compilation(code: str) -> StateError:
    """Check if Python code compiles without errors.
    
    Args:
        code: Python source code to compile
        
    Returns:
        StateError with status=0 if successful, status=1 with error message if failed
    """
    if not code or not code.strip():
        return StateError(status=1, message="Empty code provided")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    
    try:
        # Attempt to compile
        py_compile.compile(tmp_path, doraise=True)
        logger.debug("Code compilation check passed")
        return StateError(status=0, message="")
    
    except py_compile.PyCompileError as e:
        error_msg = str(e)
        logger.warning(f"Compilation error: {error_msg[:200]}")
        return StateError(status=1, message=error_msg)
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)