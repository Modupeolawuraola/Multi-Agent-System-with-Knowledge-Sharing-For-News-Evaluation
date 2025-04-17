import os
import json
os.environ["EVALUATION_MODE"] = "True"  # Set to True to bypass AWS credential checks


import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock


from src_v3.components.bias_analyzer.bias_agent import bias_analyzer_agent
from src_v3.memory.schema import GraphState

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

    # Mock methods used in the bias analyzer
    mock.query_most_structurally_similar_bias = MagicMock(return_value="Center")

    return mock


@pytest.fixture
def mock_chain():
    """Fixture to mock bias analysis chain"""
    mock = MagicMock()

    # Create a mock analysis result
    mock_result = {
        'bias': 'Center',
        'confidence_score': 75,
        'reasoning': 'The article uses neutral language and presents multiple perspectives.',
        'related_nodes': ['Article 1', 'Article 2']
    }

    mock.invoke = MagicMock(return_value=mock_result)
    return mock


def test_bias_analyzer_agent(mock_kg, mock_chain):
    """Test the bias analyzer agent with a mock chain"""

    # Create initial state with a test article
    initial_state = GraphState(articles=[SAMPLE_ARTICLE])

    # Patch all the necessary functions to avoid AWS calls
    with patch("src_v3.components.bias_analyzer.bias_agent.create_bias_analysis_chain",
               return_value=mock_chain), \
            patch("src_v3.components.bias_analyzer.bias_agent.create_llm", return_value=MagicMock()), \
            patch("src_v3.components.bias_analyzer.bias_agent.initialize_entity_extractor"), \
            patch("src_v3.components.bias_analyzer.bias_agent.extract_entities",
                  return_value=["Test Entity 1", "Test Entity 2"]), \
            patch("src_v3.components.bias_analyzer.bias_agent.diagnostic_check"):
        # Call the bias analyzer agent
        result_state = bias_analyzer_agent(initial_state, mock_kg)

    # Check that the result state has the expected structure
    assert hasattr(result_state, "articles")
    assert len(result_state.articles) == 1
    assert "bias_result" in result_state.articles[0]

    # Check bias analysis content matches our mock
    bias_result = result_state.articles[0]["bias_result"]
    assert bias_result['bias'] == 'Center'
    assert bias_result['confidence_score'] == 75
    assert 'reasoning' in bias_result
    assert 'related_nodes' in bias_result

    # Check that the state has been updated correctly
    assert result_state.current_status == "bias_analyzed"


def test_bias_analyzer_with_empty_articles(mock_kg):
    """Test the bias analyzer with empty articles list"""

    # Create initial state with empty articles list
    initial_state = GraphState(articles=[])

    # Patch necessary functions
    with patch("src_v3.components.bias_analyzer.bias_agent.diagnostic_check"), \
            patch("src_v3.components.bias_analyzer.bias_agent.create_llm", return_value=MagicMock()), \
            patch("src_v3.components.bias_analyzer.bias_agent.initialize_entity_extractor"):
        # Call the bias analyzer agent
        result_state = bias_analyzer_agent(initial_state, mock_kg)

    # Check that the result state has no articles
    assert hasattr(result_state, "articles")
    assert len(result_state.articles) == 0
    assert result_state.current_status == "bias_analyzed"  # Status is still updated


def test_bias_analyzer_exception_handling(mock_kg):
    """Test exception handling in the bias analyzer"""

    # Create initial state with a test article
    initial_state = GraphState(articles=[SAMPLE_ARTICLE])

    # Patch to make extract_entities raise an exception
    with patch("src_v3.components.bias_analyzer.bias_agent.diagnostic_check"), \
            patch("src_v3.components.bias_analyzer.bias_agent.create_llm", return_value=MagicMock()), \
            patch("src_v3.components.bias_analyzer.bias_agent.initialize_entity_extractor"), \
            patch("src_v3.components.bias_analyzer.bias_agent.extract_entities",
                  side_effect=Exception("Test exception")):
        # Call the bias analyzer agent
        result_state = bias_analyzer_agent(initial_state, mock_kg)

    # Check that the state contains no articles (since the exception prevented processing)
    assert hasattr(result_state, "articles")
    assert len(result_state.articles) == 0
    assert result_state.current_status == "bias_analyzed"  # Status is still updated


def test_bias_analyzer_json_state(mock_kg, mock_chain):
    """Test that the bias analyzer can handle GraphState passed as JSON dict"""

    # Create initial state as a dictionary
    initial_state = {
        "articles": [SAMPLE_ARTICLE],
        "current_status": "ready"
    }

    # Patch all the necessary functions
    with patch("src_v3.components.bias_analyzer.bias_agent.create_bias_analysis_chain",
               return_value=mock_chain), \
            patch("src_v3.components.bias_analyzer.bias_agent.create_llm", return_value=MagicMock()), \
            patch("src_v3.components.bias_analyzer.bias_agent.initialize_entity_extractor"), \
            patch("src_v3.components.bias_analyzer.bias_agent.extract_entities",
                  return_value=["Test Entity 1", "Test Entity 2"]), \
            patch("src_v3.components.bias_analyzer.bias_agent.diagnostic_check"):
        # Call the bias analyzer agent
        result_state = bias_analyzer_agent(initial_state, mock_kg)

    # Check that the result state has been properly converted to a GraphState
    assert not isinstance(result_state, dict)
    assert hasattr(result_state, "articles")
    assert len(result_state.articles) == 1
    assert "bias_result" in result_state.articles[0]


def test_bias_analyzer_no_knowledge_graph(mock_chain):
    """Test bias analyzer when knowledge graph is None"""

    # Create initial state
    initial_state = GraphState(articles=[SAMPLE_ARTICLE])

    # Patch necessary functions
    with patch("src_v3.components.bias_analyzer.bias_agent.create_bias_analysis_chain",
               return_value=mock_chain), \
            patch("src_v3.components.bias_analyzer.bias_agent.create_llm", return_value=MagicMock()), \
            patch("src_v3.components.bias_analyzer.bias_agent.initialize_entity_extractor"), \
            patch("src_v3.components.bias_analyzer.bias_agent.extract_entities",
                  return_value=["Test Entity 1", "Test Entity 2"]), \
            patch("src_v3.components.bias_analyzer.bias_agent.diagnostic_check"):
        # Call the bias analyzer agent with None for knowledge_graph
        result_state = bias_analyzer_agent(initial_state, None)

    # Check that processing still worked
    assert hasattr(result_state, "articles")
    assert len(result_state.articles) == 1
    assert "bias_result" in result_state.articles[0]

    # The mock_chain will return its mock result regardless, but the code should have taken
    # the branch where knowledge_graph is None