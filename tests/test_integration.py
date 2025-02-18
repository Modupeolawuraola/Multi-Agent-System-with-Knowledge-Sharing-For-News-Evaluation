
import pytest
from src.workflow.graph import create_workflow
from src.memory.schema import GraphState


def test_complete_workflow():
    """Test the entire workflow from news collection to storage"""
    workflow = create_workflow()

    initial_state = GraphState(
        knowledge_graph={},
        articles=[],
        current_status="ready"
    )

    # Use .invoke() instead of .run()
    final_state = workflow.invoke(initial_state)

    # Check workflow completion
    assert final_state['current_status'] in ['retrieval_complete', 'workflow_complete']
    assert 'articles' in final_state  # Verify articles exist

    # Check if articles have bias analysis
    if final_state['articles']:
        assert 'bias_analysis' in final_state['articles'][0]