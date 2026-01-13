"""Agent responsible for transpiling Java code to Python and fixing errors."""

import re
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from loguru import logger
from core.state import State, StateError
from core.tools.compiler import check_compilation


class TranspileAgent:
    """Transpiles Java to Python and iteratively fixes compilation errors."""

    def __init__(
        self,
        model: ChatOpenAI,
        system_prompt: str,
        transpile_user_prompt: str,
        error_prompts: dict,
    ):
        """Initialize the transpile agent.
        
        Args:
            model: LLM instance for code generation
            system_prompt: System-level instructions
            transpile_user_prompt: Template for initial transpilation
            error_prompts: Dict mapping error types to fix prompts
        """
        self.name = "transpile"
        self.model = model
        self.system_prompt = system_prompt
        self.transpile_user_prompt = transpile_user_prompt
        self.error_prompts = error_prompts
        logger.debug(f"Initialized {self.name} agent")

    def run(self, state: State) -> State:
        """Transpile code or fix errors based on current state.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with transpiled code and error status
        """
        is_retry = state["current_iterations"] > 0
        
        if is_retry:
            logger.warning(
                f"[{self.name}] Retry attempt {state['current_iterations']} - fixing errors"
            )
            state = self._fix_errors(state)
        else:
            logger.info(f"[{self.name}] Starting initial transpilation")
            state = self._initial_transpile(state)
        
        # Check compilation
        error = check_compilation(state["code"])
        state["last_error"] = error
        state["current_iterations"] += 1
        
        if error.status == 0:
            logger.success(f"[{self.name}] Code compiled successfully!")
        else:
            logger.error(f"[{self.name}] Compilation failed: {error.message[:200]}")
        
        return state

    def _initial_transpile(self, state: State) -> State:
        """Perform initial transpilation from Java to Python.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with initial transpiled code
        """
        user_prompt = self.transpile_user_prompt.format(
            plan=state["plan"],
            original_code=state["original_code"]
        )
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.model.invoke(messages)
        code = self._extract_code(response.content)
        
        state["code"] = code
        logger.debug(f"Generated {len(code)} chars of Python code")
        
        return state

    def _fix_errors(self, state: State) -> State:
        """Fix compilation errors in the transpiled code.
        
        Args:
            state: Current workflow state with error information
            
        Returns:
            Updated state with fixed code attempt
        """
        error_type = state["last_error"].status
        error_message = state["last_error"].message
        
        # Use the appropriate error prompt
        error_prompt_template = self.error_prompts.get(error_type, self.error_prompts[1])
        error_prompt = error_prompt_template.format(trace=error_message)
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"{error_prompt}\n\n```python\n{state['code']}\n```"),
        ]
        
        response = self.model.invoke(messages)
        fixed_code = self._extract_code(response.content)
        
        state["code"] = fixed_code
        logger.debug(f"Generated fix attempt ({len(fixed_code)} chars)")
        
        return state

    def _extract_code(self, llm_response: str) -> str:
        """Extract Python code from LLM response (removes markdown fences).
        
        Args:
            llm_response: Raw LLM output possibly containing markdown
            
        Returns:
            Clean Python code
        """
        # Match ```python ... ``` blocks
        pattern = r"```python\s*\n(.*?)\n```"
        matches = re.findall(pattern, llm_response, re.DOTALL)
        
        if matches:
            code = matches[0].strip()
            logger.debug("Extracted code from markdown fence")
            return code
        
        # Fallback: return the whole response
        logger.warning("No markdown fence found, using full response as code")
        return llm_response.strip()