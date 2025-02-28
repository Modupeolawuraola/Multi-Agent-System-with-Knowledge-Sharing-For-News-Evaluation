from ...memory.schema import GraphState


def UpdaterAgent(state: GraphState) -> GraphState:  # Define the function
    """Agent specifically for updating knowledge graph with new data"""
    new_state = state.copy()

    #making sure articles exists even if there is an error
    if 'articles' not in new_state:
        new_state['articles'] = []

    try:
        current_knowledge = state['knowledge_graph']
        new_data = state.get('retrieved_articles', [])

        updated_knowledge = current_knowledge.copy()

        #initialize articles in knowledge graph if its doesnt exist
        if 'articles' not in updated_knowledge:
            updated_knowledge['articles'] = []

        updated_knowledge['articles'].extend(new_data)

        new_state['knowledge_graph'] = updated_knowledge
        new_state['current_status'] = 'update_complete'
        new_state['updated_data'] = new_data

    except Exception as e:
        print(f"Error in update: {e}")
        #preserve articles even on error
        if 'articles' not in new_state:
            new_state['articles'] = []
        new_state['current_status'] = 'update_failed'
        new_state['error'] = str(e)

    return new_state