import os
os.environ["EVALUATION_MODE"] = "False"
import pytest
from unittest.mock import patch, MagicMock
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.bias_analyzer_agent.bias_agent import bias_analyzer_agent
from src.memory.schema import GraphState
import logging


@pytest.fixture
def mock_chain():
    """Create a mock chain that returns bias analysis results"""
    mock = MagicMock()
    mock.invoke.return_value = {
        "confidence_score": 75,
        "findings": [
            "The article uses loaded language",
            "Source attribution is inconsistent"
        ],
        "overall_assessment": "The article shows moderate bias",
        "recommendations": [
            "Use more neutral language",
            "Include diverse perspectives"
        ]
    }
    return mock

@pytest.fixture
def mock_bedrock():
    with patch('boto3.client') as mock_client:
        # Setup mock client behavior
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance


def test_bias_analyzer_agent(mock_bedrock,mock_chain):
    """Test bias analyzer agent."""
    # Patch the create_bias_analysis_chain function
    with patch('src.components.bias_analyzer_agent.tools.create_bias_analysis_chain') as mock_create_chain:
        mock_create_chain.return_value = mock_chain

        # Create test state with articles (using plural consistently)
        initial_state = GraphState(
            knowledge_graph={},
            articles=[{
                'title': 'Test Article',
                'content': 'This is extremely biased and shocking',
                'source': 'Test Source'
            }],
            current_status="ready"
        )

        # Run the agent
        new_state = bias_analyzer_agent(initial_state)

        # Check results - use attribute access
        assert new_state.current_status == "bias_analysis_complete"
        assert hasattr(new_state, "articles")
        assert len(new_state.articles) == 1
        assert 'bias_analysis' in new_state.articles[0]


def test_bias_analyzer_result_structure(mock_chain):
    """Test if bias analysis returns correct structure"""
    # Patch the create_bias_analysis_chain function in bias_agent, not tools
    with patch('src.components.bias_analyzer_agent.bias_agent.create_bias_analysis_chain') as mock_create_chain:
        # Configure mock to return a predictable result
        mock_chain.invoke.return_value = {
            "confidence_score": 75,
            "findings": ["Test finding"],
            "overall_assessment": "Test assessment",
            "recommendations": ["Test recommendation"]
        }
        mock_create_chain.return_value = mock_chain

        # Create test state with articles
        initial_state = GraphState(
            knowledge_graph={},
            articles=[{
                'title': 'Test Article',
                'content': 'Normal Article content',
                'source': 'Test Source'
            }],
            current_status="ready"
        )

        # Run the agent
        new_state = bias_analyzer_agent(initial_state)

        # Check structure of results
        assert 'bias_analysis' in new_state.articles[0]
        bias_analysis = new_state.articles[0]['bias_analysis']
        assert 'confidence_score' in bias_analysis
        assert 'findings' in bias_analysis
        assert 'overall_assessment' in bias_analysis
        assert 'recommendations' in bias_analysis

def test_bias_analyzer_with_empty_articles():
    """Test bias analyzer with empty articles list"""
    # Create test state with empty articles list
    initial_state = GraphState(
        knowledge_graph={},
        articles=[],
        current_status="ready"
    )

    # Run the agent
    new_state = bias_analyzer_agent(initial_state)

    # Check error handling - use attribute access
    assert new_state.current_status == "no_articles_to_analyze"
    assert hasattr(new_state, "error") or new_state.error is None
    assert hasattr(new_state, "articles")


def test_bias_analyzer_with_backward_compatibility():
    """Test bias analyzer with article (singular) for backward compatibility"""
    # Patch the create_bias_analysis_chain function
    with patch('src.components.bias_analyzer_agent.bias_agent.create_bias_analysis_chain') as mock_create_chain:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {
            "confidence_score": 75,
            "findings": ["Test finding"],
            "overall_assessment": "Test assessment",
            "recommendations": ["Test recommendation"]
        }
        mock_create_chain.return_value = mock_chain

        # Use a dictionary instead of GraphState directly
        initial_state = {
            "knowledge_graph": {},
            "article": [{
                'title': 'Test Article',
                'content': 'Test content',
                'source': 'Test Source'
            }],
            "current_status": "ready"
        }

        # Run the agent
        new_state = bias_analyzer_agent(initial_state)

        # Check results
        assert new_state.current_status == "bias_analysis_complete"
        assert hasattr(new_state, "articles")
        assert len(new_state.articles) == 1
        assert 'bias_analysis' in new_state.articles[0]
