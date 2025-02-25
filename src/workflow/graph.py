from langgraph.graph import StateGraph, START, END
from ..memory.schema import GraphState
from ..components.news_collector_agent.news_agent import new_collector_Agent
from ..components.bias_analyzer_agent.bias_agent import bias_analyzer_agent
from ..components.retriever_Agent.retriever_agent import RetrieverAgent
from ..components.updater_agent.updater_agent import UpdaterAgent

def create_workflow():
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("collector", new_collector_Agent)
    workflow.add_node("analyzer", bias_analyzer_agent)
    workflow.add_node("updater", UpdaterAgent)
    workflow.add_node("retriever", RetrieverAgent)



    # Add edges
    workflow.add_edge(START, "collector")
    workflow.add_edge("collector", "analyzer")
    workflow.add_edge("analyzer", "updater")
    workflow.add_edge("updater", "retriever")
    workflow.add_edge("retriever", END)

    return workflow.compile()