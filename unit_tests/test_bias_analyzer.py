import pytest
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.components.bias_analyzer_agent.ag import bias_analyzer_agent
from src.memory.schema import GraphState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bias_analyzer_agent():
    """Test bias analyzer agent."""
    logger.info("Starting Bias Analyzer Agent test")
    initial_state = GraphState(
        knowledge_graph={},
        articles=[{
            'title': 'Test Article',
            'content': 'This is extremely biased and shocking',
            'source': 'Test Source',
            'date': '2025-02-22'
        }],
        current_status="ready"
    )
    logger.info("Created initial state")
    new_state = bias_analyzer_agent(initial_state)
    logger.info(f'Received new state with status: {new_state['current_status']}')
    assert new_state['current_status'] == "bias_analysis_complete"
    assert 'bias_analysis' in new_state['articles'][0]


def test_bias_analyzer_result_structure():
    """Test if bias analysis returns correct structure"""
    logger.info("Starting Bias Analyzer Agent test")
    initial_state = GraphState(
        knowledge_graph={},
        articles=[{  # Using 'articles' consistently
            'title': 'Test Article',
            'content': 'Normal Article content',
            'source': 'Test Source',
            'data' : '2025-02-22'
        }],
        current_status="ready"
    )
    logger.info("Created initial state for structure test")
    new_state = bias_analyzer_agent(initial_state)
    assert 'bias_analysis' in new_state['articles'][0]

if __name__ == '__main__':
    pytest.main([__file__, "-v"])