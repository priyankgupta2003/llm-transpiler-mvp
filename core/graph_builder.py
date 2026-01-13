"""Utilities for building LangGraph workflows."""

from typing import Callable, Dict, Any
from langgraph.graph import StateGraph, END
from core.state import State
from loguru import logger


class GraphBuilder:
    """Simplified builder for creating LangGraph state machines."""

    def __init__(self):
        """Initialize the graph builder with a State schema."""
        self.graph = StateGraph(State)
        self.entry_point = None
        logger.debug("GraphBuilder initialized")

    def add_node(self, agent: Any) -> None:
        """Add an agent as a node in the graph.
        
        Args:
            agent: Agent instance with a `name` attribute and callable `run` method
        """
        self.graph.add_node(agent.name, agent.run)
        logger.debug(f"Added node: {agent.name}")

    def set_entry_point(self, agent: Any) -> None:
        """Set the entry point for the graph.
        
        Args:
            agent: Agent to use as the starting point
        """
        self.entry_point = agent.name
        self.graph.set_entry_point(agent.name)
        logger.debug(f"Set entry point: {agent.name}")

    def add_edge(self, from_agent: Any, to_agent: Any) -> None:
        """Add a directed edge between two agents.
        
        Args:
            from_agent: Source agent
            to_agent: Destination agent
        """
        self.graph.add_edge(from_agent.name, to_agent.name)
        logger.debug(f"Added edge: {from_agent.name} -> {to_agent.name}")

    def add_conditional_edge(
        self,
        source_agent: Any,
        condition: Callable[[State], str],
        mapping: Dict[str, str],
    ) -> None:
        """Add a conditional edge with routing logic.
        
        Args:
            source_agent: Agent to route from
            condition: Function that returns a routing key based on state
            mapping: Dictionary mapping condition results to target node names or END
        """
        self.graph.add_conditional_edges(source_agent.name, condition, mapping)
        logger.debug(f"Added conditional edge from {source_agent.name}: {mapping}")

    def compile(self) -> StateGraph:
        """Compile the graph into an executable workflow.
        
        Returns:
            Compiled StateGraph ready for execution
        """
        compiled = self.graph.compile()
        logger.info("Graph compiled successfully")
        return compiled