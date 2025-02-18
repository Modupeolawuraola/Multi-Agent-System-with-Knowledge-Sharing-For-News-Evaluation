from ...memory.schema import GraphState


def UpdaterAgent(state: GraphState) -> GraphState:  # Define the function
    """Agent specifically for updating knowledge graph with new data"""
    new_state = state.copy()

    try:
        current_knowledge = state['knowledge_graph']
        new_data = state.get('retrieved_articles', [])

        updated_knowledge = current_knowledge.copy()
        updated_knowledge['articles'].extend(new_data)

        new_state['knowledge_graph'] = updated_knowledge
        new_state['current_status'] = 'update_complete'
        new_state['updated_data'] = new_data

    except Exception as e:
        print(f"Error in update: {e}")
        new_state['current_status'] = 'update_failed'
        new_state['error'] = str(e)

    return new_state