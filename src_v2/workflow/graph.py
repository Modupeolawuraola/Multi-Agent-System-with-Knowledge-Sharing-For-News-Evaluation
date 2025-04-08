
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from src_v2.components.kg_builder.kg_builder import KnowledgeGraph
from src_v2.components.bias_analyzer.bias_agent import bias_analyzer_agent
from src_v2.components.fact_checker.fact_checker import fact_checker_agent
import os


# Define state class with proper annotations for channels that receive multiple updates
class GraphState(BaseModel):
    articles: List[Dict[str, Any]] = Field(default_factory=list)
    news_query: Optional[str] = None
    bias_query: Optional[str] = None
    fact_check_result: Optional[Dict[str, Any]] = None
    bias_analysis_result: Optional[Dict[str, Any]] = None
    current_status: str = "ready"
    error: Optional[str] = None


def create_workflow(evaluation_mode=False):
    """
    Create the workflow graph with direct KG interaction.

    Args:
        evaluation_mode: Whether to run in evaluation mode

    Returns:
        Compiled workflow
    """
    # Check environment variable for evaluation mode
    if os.environ.get("EVALUATION_MODE", "false").lower() == "true":
        evaluation_mode = True

    # Initialize Knowledge Graph (shared between all nodes)
    kg = KnowledgeGraph()

    # Create the workflow graph
    workflow = StateGraph(GraphState)

    # Add all nodes
    workflow.add_node("start", lambda x: x)  # Identity node for conditional branching

    # Add nodes with KG parameter
    workflow.add_node("kg_builder", lambda state: build_kg(state, kg))
    workflow.add_node("bias_analyzer", lambda state: bias_analyzer_agent(state, kg))
    workflow.add_node("fact_checker", lambda state: fact_checker_agent(state, kg))

    # Define conditional routing from start node
    def route_start(state):
        """Determine first step based on state"""
        if state.news_query:
            return "fact_check_path"
        elif state.bias_query:
            return "bias_path"
        return "kg_builder_path"

    # Connect the start node with high-level path selection
    workflow.add_conditional_edges(
        "start",
        route_start,
        {
            "fact_check_path": "fact_checker",
            "bias_path": "bias_analyzer",
            "kg_builder_path": "kg_builder"
        }
    )

    # Define the main workflow paths
    workflow.add_edge("kg_builder", "bias_analyzer")
    workflow.add_edge("bias_analyzer", "fact_checker")
    workflow.add_edge("fact_checker", END)

    # Direct paths to end
    workflow.add_edge("bias_analyzer", END)
    workflow.add_edge("fact_checker", END)

    # Set entry point
    workflow.set_entry_point("start")

    return workflow.compile()


def build_kg(state, kg):
    """
    Build knowledge graph from news articles.
    This replaces the functionality of the news collector agent.

    Args:
        state: Current state
        kg: Knowledge Graph instance

    Returns:
        Updated state
    """
    new_state = state.copy()

    try:
        # If we have articles in the state, add them to the KG
        if state.articles:
            for article in state.articles:
                kg.add_article(article)
            new_state.current_status = "kg_updated"
        # Otherwise, we could fetch new articles from a news API here
        else:
            # In a real implementation, you would fetch articles from news API
            # and add them to the KG
            new_state.current_status = "no_articles_provided"
    except Exception as e:
        new_state.error = str(e)
        new_state.current_status = "kg_builder_error"

    return new_state