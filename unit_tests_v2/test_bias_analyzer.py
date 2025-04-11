import os

os.environ["EVALUATION_MODE"] = "False"
import pytest
from unittest.mock import patch, MagicMock
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src_v2.components.bias_analyzer.bias_agent import bias_analyzer_agent
from src_v2.memory.schema import GraphState
from src_v2.components.kg_builder.kg_builder import KnowledgeGraph

# Sample test article
SAMPLE_ARTICLE = {
    "title": "Test Article Title",
    "content": "This is a test article content with a moderate political perspective.",
    "source": "Test News Source",
    "date": "2025-04-08",
    "url": "https://example.com/test-article"
}


@pytest.fixture
def mock_kg():
    """Fixture to mock Knowledge Graph"""
    mock = MagicMock()

    # Mock the add_bias_analysis method
    mock.add_bias_analysis = MagicMock(return_value=True)

    return mock


def test_bias_analyzer_agent(mock_kg):
    """Test the bias analyzer agent with a mock AWS client"""

    # Set up test environment variables
    os.environ["TESTING"] = "true"

    # Create initial state with a test article
    initial_state = GraphState(articles=[SAMPLE_ARTICLE])

    # Create a mock analysis result
    mock_analysis_result = {
        'confidence_score': 75,
        'overall_assessment': 'The article shows minimal bias',
        'findings': ['Uses neutral language', 'Presents multiple perspectives']
    }

    # Instead of trying to mock the chain, directly patch the function that uses it
    # Bypass all the chain creation and AWS stuff completely
    with patch("src_v2.components.bias_analyzer.bias_agent.create_bias_analysis_chain") as mock_create_chain:
        # Create a mock chain that returns our desired result
        mock_chain = MagicMock()
        mock_chain.invoke = MagicMock(return_value=mock_analysis_result)
        mock_create_chain.return_value = mock_chain

        # Also patch the diagnostic check to avoid AWS credential checks
        with patch("src_v2.components.bias_analyzer.bias_agent.diagnostic_check"):
            result_state = bias_analyzer_agent(initial_state, mock_kg)

    # Check that the result state has the expected structure
    assert hasattr(result_state, "articles")
    assert len(result_state.articles) == 1
    assert "bias_analysis" in result_state.articles[0]

    # Check bias analysis content
    assert result_state.articles[0]["bias_analysis"] == mock_analysis_result

    # Check that the analyzer added the bias analysis to KG
    mock_kg.add_bias_analysis.assert_called_once()


def test_bias_analyzer_result_structure(mock_kg):
    """Test that the bias analyzer returns properly structured results"""

    # Set up test environment variables
    os.environ["TESTING"] = "true"

    # Create initial state with a test article
    initial_state = GraphState(articles=[SAMPLE_ARTICLE])

    # Create a mock analysis result
    mock_analysis_result = {
        'confidence_score': 75,
        'overall_assessment': 'The article shows minimal bias',
        'findings': ['Uses neutral language', 'Presents multiple perspectives']
    }

    # Bypass all the chain creation and AWS stuff completely
    with patch("src_v2.components.bias_analyzer.bias_agent.create_bias_analysis_chain") as mock_create_chain:
        # Create a mock chain that returns our desired result
        mock_chain = MagicMock()
        mock_chain.invoke = MagicMock(return_value=mock_analysis_result)
        mock_create_chain.return_value = mock_chain

        # Also patch the diagnostic check to avoid AWS credential checks
        with patch("src_v2.components.bias_analyzer.bias_agent.diagnostic_check"):
            result_state = bias_analyzer_agent(initial_state, mock_kg)

    # Verify the structure of the bias analysis
    bias_analysis = result_state.articles[0]["bias_analysis"]
    assert "confidence_score" in bias_analysis
    assert "overall_assessment" in bias_analysis
    assert "findings" in bias_analysis

    # Verify types
    assert isinstance(bias_analysis["confidence_score"], (int, float))
    assert isinstance(bias_analysis["overall_assessment"], str)
    assert isinstance(bias_analysis["findings"], list)


def test_bias_analyzer_with_empty_articles(mock_kg):
    """Test the bias analyzer with empty articles list"""

    # Create initial state with empty articles list
    initial_state = GraphState(articles=[])

    # Bypass AWS credential check
    with patch("src_v2.components.bias_analyzer.bias_agent.diagnostic_check"):
        # Call the bias analyzer agent
        result_state = bias_analyzer_agent(initial_state, mock_kg)

    # Check that the result state has the right status
    assert result_state.current_status == 'no_articles_to_analyze'
    assert hasattr(result_state, "articles")
    assert len(result_state.articles) == 0


def test_bias_analyzer_with_bias_query(mock_kg):
    """Test the bias analyzer with a direct bias query"""

    # Set up test environment variables
    os.environ["TESTING"] = "true"

    # Create initial state with a bias query
    initial_state = GraphState(bias_query="Is the media coverage of climate change biased?")

    # Create a mock analysis result
    mock_analysis_result = {
        'confidence_score': 85,
        'overall_assessment': 'Media coverage shows some bias',
        'findings': ['Emphasis on specific viewpoints', 'Limited counter-perspectives']
    }

    # Bypass all the chain creation and AWS stuff completely
    with patch("src_v2.components.bias_analyzer.bias_agent.create_bias_analysis_chain") as mock_create_chain:
        # Create a mock chain that returns our desired result
        mock_chain = MagicMock()
        mock_chain.invoke = MagicMock(return_value=mock_analysis_result)
        mock_create_chain.return_value = mock_chain

        # Also patch the diagnostic check to avoid AWS credential checks
        with patch("src_v2.components.bias_analyzer.bias_agent.diagnostic_check"):
            result_state = bias_analyzer_agent(initial_state, mock_kg)

    # Check that we have bias analysis results directly in the state
    assert hasattr(result_state, "bias_analysis_result")
    assert result_state.bias_analysis_result is not None
    assert result_state.bias_analysis_result["analysis"] == mock_analysis_result
