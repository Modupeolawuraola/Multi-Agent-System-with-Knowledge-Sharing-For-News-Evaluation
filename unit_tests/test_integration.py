
import pytest
from src.workflow.graph import create_workflow
from src.memory.schema import GraphState


def test_complete_workflow():
    """Test the entire workflow from news collection to storage"""
    workflow = create_workflow()

    initial_state = GraphState(
        knowledge_graph={},
        articles = [],
        last_retrieved_date= None,
        current_status="ready",
        error= None
    )

    # Use .invoke()
    final_state = workflow.invoke(initial_state)

    # Check workflow completion
    assert final_state['current_status'] in ['retrieval_complete', 'workflow_complete']

    #check knowledge_graph instead of articles
    assert 'knowledge_graph' in final_state
    assert 'articles' in final_state['knowledge_graph']

