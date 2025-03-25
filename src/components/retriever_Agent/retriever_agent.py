from ...memory.schema import GraphState
from datetime import datetime, timedelta


def RetrieverAgent(state: GraphState) -> GraphState:
    """Agent specifically for retrieving data from knowledge graph"""

    if isinstance(state, dict):
        state = GraphState(**state)

    # create new state copy for immutability
    new_state = state.copy()
    try:
        # get data from knowledge graph
        knowledge = state.knowledge_graph

        # retrieve specific data (example)
        retrieved_articles = knowledge.get('articles', []) if knowledge else []
        last_retrieved = state.last_retrieved_date if hasattr(state, "last_retrieved_date") else None

        if last_retrieved:
            filtered_data = [
                article for article in retrieved_articles
                if article['date'] > last_retrieved
            ]
        else:
            filtered_data = retrieved_articles

        # update state
        new_state.retrieved_articles = filtered_data
        new_state.current_status = 'retrieval_complete'

    except Exception as e:
        print(f"Error in retrieval: {e}")
        new_state.current_status = 'retrieval_failed'
        new_state.retrieved_articles = str(e)

    return new_state
