"""Python code formatting tool using Black."""

import black
from loguru import logger


def python_format(code: str) -> str:
    """Format Python code using Black formatter for PEP8 compliance.
    
    Args:
        code: Python source code to format
        
    Returns:
        Formatted Python code
    """
    try:
        mode = black.Mode(
            target_versions={black.TargetVersion.PY312},
            line_length=88,
        )
        formatted = black.format_str(code, mode=mode)
        logger.debug("Code formatted with Black")
        return formatted
    
    except Exception as e:
        logger.warning(f"Black formatting failed: {e}, returning original code")
        return code