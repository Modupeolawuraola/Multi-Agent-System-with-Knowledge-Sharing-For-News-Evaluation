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

    # Define routing function
    def get_next_step(state: GraphState) -> str:
        status_map = {
            'ready': "collector",
            'collection_complete': "analyzer",
            'analysis_complete': "updater",
            'update_complete': "retriever",
            'retrieval_complete': END
        }
        return status_map.get(state['current_status'], state['current_status'])

    # Add edges
    workflow.add_edge(START, get_next_step)
    workflow.add_edge("collector", get_next_step)
    workflow.add_edge("analyzer", get_next_step)
    workflow.add_edge("updater", get_next_step)
    workflow.add_edge("retriever", get_next_step)

    return workflow.compile()