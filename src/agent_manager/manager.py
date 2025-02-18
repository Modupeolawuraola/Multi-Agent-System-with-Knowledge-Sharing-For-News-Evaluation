from langgraph.graph import StateGraph
from ..memory.schema import GraphState
#import the main agent function from bias_agent.py
from ..components.bias_analyzer_agent import bias_analyzer_node
class AgentManager:
    def __init__(self):
        self.graph = StateGraph(GraphState)

    def register_agents(self):
        """Register all agents as nodes"""
        self.graph.add_node('bias_analyzer', bias_analyzer_node)

    def define_Workflow(self):
        """define transitions for bias analyzer"""
        self.graph.add_edge("bias_analyzer", "next_agent", self.s)