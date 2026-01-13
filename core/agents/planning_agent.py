"""Agent responsible for generating transpilation plans."""

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from loguru import logger
from core.state import State


class PlanningAgent:
    """Generates a detailed step-by-step transpilation strategy."""

    def __init__(self, model: ChatOpenAI, system_prompt: str, planning_user_prompt: str):
        """Initialize the planning agent.
        
        Args:
            model: LLM instance for generating plans
            system_prompt: System-level instructions
            planning_user_prompt: Template for user messages
        """
        self.name = "planning"
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt_template = planning_user_prompt
        logger.debug(f"Initialized {self.name} agent")

    def run(self, state: State) -> State:
        """Generate a migration roadmap based on the summary and original code.
        
        Args:
            state: Current workflow state containing summary and original_code
            
        Returns:
            Updated state with plan field populated
        """
        logger.info(f"[{self.name}] Starting migration planning")
        
        user_prompt = self.user_prompt_template.format(
            summary=state["summary"],
            original_code=state["original_code"]
        )
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.model.invoke(messages)
        plan = response.content
        
        logger.success(f"[{self.name}] Plan generated ({len(plan)} chars)")
        logger.debug(f"Plan preview: {plan[:200]}...")
        
        state["plan"] = plan
        return state