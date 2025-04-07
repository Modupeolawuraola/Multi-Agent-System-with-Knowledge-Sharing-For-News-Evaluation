from typing import Annotated, Dict, List, Optional, Any
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from src.components.news_collector_agent.news_agent import new_collector_Agent
from src.components.bias_analyzer_agent.bias_agent import bias_analyzer_agent
from src.components.retriever_Agent.retriever_agent import RetrieverAgent
from src.components.updater_agent.updater_agent import UpdaterAgent
from src.components.fact_checker_agent.fact_checker_Agent import fact_checker_agent
import os


# Define state class with proper annotations for channels that receive multiple updates
class GraphState(BaseModel):
    knowledge_graph: Dict[str, Any] = Field(default_factory=lambda: {"articles": []})
    articles: List[Dict[str, Any]] = Field(default_factory=list)
    news_query: Optional[str] = None
    fact_check_result: Optional[Dict[str, Any]] = None
    last_retrieved_date: Optional[str] = None
    current_status: str = "ready"
    bias_agent: Optional[Any] = None
    error: Optional[str] = None


def create_workflow(evaluation_mode=False):
    """
    Create the workflow graph.

    Args:
        evaluation_mode: Whether to run in evaluation mode (skip news collector)

    Returns:
        Compiled workflow
    """
    # Check environment variable for evaluation mode
    if os.environ.get("EVALUATION_MODE", "false").lower() == "true":
        evaluation_mode = True

    # Create the workflow graph
    workflow = StateGraph(GraphState)

    # Add all nodes
    workflow.add_node("start", lambda x: x)  # Identity node for conditional branching
    workflow.add_node("collector", new_collector_Agent)
    workflow.add_node("analyzer", bias_analyzer_agent)
    workflow.add_node("fact_checker", fact_checker_agent)
    workflow.add_node("updater", UpdaterAgent)
    workflow.add_node("retriever", RetrieverAgent)

    # Define conditional routing from start node
    def route_start(state):
        """Determine first step based on state"""
        # access pydantic model attributes directly
        if state.news_query:
            return "fact_check_path"
        # In evaluation mode with articles, or normal collection path
        return "collection_path"

    # Connect the start node with high-level path selection
    workflow.add_conditional_edges(
        "start",
        route_start,
        {
            "fact_check_path": "fact_checker",
            "collection_path": "collection_start"
        }
    )

    # Add a collection start node for further routing
    workflow.add_node("collection_start", lambda x: x)

    # Define the collection path routing
    def route_collection(state):
        """Determine where to start in the collection path"""
        # If in evaluation mode and articles are provided, skip collection
        if evaluation_mode and state.articles:
            return "analyzer"
        # Otherwise start with collection
        return "collector"

    # Connect collection start with conditional routing
    workflow.add_conditional_edges(
        "collection_start",
        route_collection,
        {
            "analyzer": "analyzer",
            "collector": "collector"
        }
    )

    # Define the main collection workflow
    workflow.add_edge("collector", "analyzer")
    workflow.add_edge("analyzer", "updater")
    workflow.add_edge("updater", "retriever")
    workflow.add_edge("retriever", END)

    # Define the direct fact-checking path
    workflow.add_edge("fact_checker", END)

    # Set entry point
    workflow.set_entry_point("start")

    return workflow.compile()
