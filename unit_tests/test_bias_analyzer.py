import pytest
from src.components.bias_analyzer_agent.bias_agent import bias_analyzer_agent  #
from src.memory.schema import GraphState
import logging


def test_bias_analyzer_agent():
    """Test bias analyzer agent."""
    initial_state = GraphState(
        knowledge_graph={},
        articles=[{
            'title': 'Test Article',
            'content': 'This is extremely biased and shocking',
            'source': 'Test Source'
        }],
        current_status="ready"
    )
    new_state = bias_analyzer_agent(initial_state)
    assert new_state['current_status'] == "bias_analysis_complete"


def test_bias_analyzer_result_structure():
    """Test if bias analysis returns correct structure"""
    initial_state = GraphState(
        knowledge_graph={},
        articles=[{  # Using 'articles' consistently
            'title': 'Test Article',
            'content': 'Normal Article content',
            'source': 'Test Source'
        }],
        current_status="ready"
    )
    new_state = bias_analyzer_agent(initial_state)
    assert 'bias_analysis' in new_state['articles'][0]