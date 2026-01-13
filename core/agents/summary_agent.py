"""Agent responsible for summarizing Java source code."""

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from loguru import logger
from core.state import State


class SummaryAgent:
    """Analyzes Java code and produces a concise technical summary."""

    def __init__(self, model: ChatOpenAI, system_prompt: str, summary_user_prompt: str):
        """Initialize the summary agent.
        
        Args:
            model: LLM instance for generating summaries
            system_prompt: System-level instructions
            summary_user_prompt: Template for user messages
        """
        self.name = "summary"
        self.model = model
        self.system_prompt = system_prompt
        self.user_prompt_template = summary_user_prompt
        logger.debug(f"Initialized {self.name} agent")

    def run(self, state: State) -> State:
        """Generate a technical summary of the Java source code.
        
        Args:
            state: Current workflow state containing original_code
            
        Returns:
            Updated state with summary field populated
        """
        logger.info(f"[{self.name}] Starting code summarization")
        
        user_prompt = self.user_prompt_template.format(
            source_code=state["original_code"]
        )
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.model.invoke(messages)
        summary = response.content
        
        logger.success(f"[{self.name}] Summary generated ({len(summary)} chars)")
        logger.debug(f"Summary preview: {summary[:200]}...")
        
        state["summary"] = summary
        return state