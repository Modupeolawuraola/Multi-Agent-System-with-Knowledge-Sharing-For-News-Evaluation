from langgraph.graph import StateGraph
from ..memory.schema import GraphState
# Import the main agent function from bias_agent.py
from src.components.bias_analyzer_agent import bias_analyzer_agent
from src.components.fact_checker_agent import fact_checker_agent
from src.components.updater_agent import UpdaterAgent
from src.components.retriever_Agent import RetrieverAgent

from .transistions import TransitionManager



class AgentManager:
    def __init__(self):
        self.graph = StateGraph(GraphState)

    def register_agents(self):
        """Register all agents as nodes"""
        self.graph.add_node('bias_analyzer', bias_analyzer_agent)
        self.graph.add_node('fact_checker', fact_checker_agent)
        self.graph.add_node('updater', UpdaterAgent)
        self.graph.add_node('retriever', RetrieverAgent)

    def define_workflow(self):
        """Define transitions for the workflow"""
        # Add transition from bias_analyzer based on status
        self.graph.add_conditional_edges(
            "bias_analyzer",
            TransitionManager.route_after_bias_analysis
        )

        # Add transition from fact_checker based on status
        self.graph.add_conditional_edges(
            "fact_checker",
            TransitionManager.route_after_fact_check
        )

        # Add final transitions
        self.graph.add_edge("updater", "retriever")
        self.graph.add_edge("retriever", END)