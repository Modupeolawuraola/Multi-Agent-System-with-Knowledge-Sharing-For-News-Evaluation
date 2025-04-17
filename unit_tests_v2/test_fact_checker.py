import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import modules to test
from src_v3.components.fact_checker.fact_checker_Agent import fact_checker_agent
from src_v3.memory.schema import GraphState
from src_v3.components.fact_checker.tools import (
    extract_entities_from_claim,
    create_factcheck_chain,
    parse_llm_response
)


@pytest.fixture
def mock_bedrock():
    with patch('boto3.client') as mock_client:
        # Setup mock client behavior
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_llm():
    llm = MagicMock()

    # Set up different responses based on the input
    def side_effect(input_data):
        # Mock JSON response for fact check chain
        if isinstance(input_data, dict) and 'claim' in input_data:
            return MagicMock(
                content=json.dumps({
                    "verdict": "True",
                    "confidence_score": 85,
                    "reasoning": "Multiple reliable sources confirm the claim.",
                    "supporting_nodes": ["Company X", "Q3 Growth", "Financial Report"]
                })
            )
        else:
            return MagicMock(content="{}")

    llm.invoke.side_effect = side_effect
    return llm


@pytest.fixture
def mock_kg():
    """Mock KnowledgeGraph for testing"""
    mock = MagicMock()

    # Explicitly add the methods that will be called
    mock.add_fact_check_result = MagicMock(return_value=True)
    mock.retrieve_related_facts_text = MagicMock(
        return_value="Company X reported 20% growth in Q3. This was confirmed in their financial statement.")
    mock.retrieve_related_articles = MagicMock(return_value=[
        {
            "title": "Company X Quarterly Report",
            "source_name": "Financial Times",
            "url": "https://example.com/company-x-q3",
            "published_at": "2025-02-15T10:00:00Z",
            "content": "Company X reported 20% growth in Q3. CEO John Smith announced plans to expand to Europe."
        }
    ])

    return mock


@pytest.fixture
def test_article():
    return {
        'title': 'Company X Reports Strong Growth',
        'content': 'Company X reported 20% growth in Q3. CEO John Smith said the company plans to expand to Europe next year.',
        'source': 'Business News Daily',
        'date': '2025-02-15T12:00:00Z',
        'url': 'https://example.com/business-news'
    }


def test_extract_entities(mock_llm):
    """Test entity extraction from claim text."""
    with patch('src_v3.components.fact_checker.tools.transformer') as mock_transformer:
        # Setup mock graph docs with entities
        mock_graph = MagicMock()
        mock_node1 = MagicMock()
        mock_node1.properties = {"name": "Company X"}
        mock_node1.id = "1"

        mock_node2 = MagicMock()
        mock_node2.properties = {"name": "John Smith"}
        mock_node2.id = "2"

        mock_graph.nodes = [mock_node1, mock_node2]
        mock_transformer.convert_to_graph_documents.return_value = [mock_graph]

        claim_text = "Company X reported 20% growth in Q3"

        # Mock the transformer global variable
        with patch('src_v3.components.fact_checker.tools.transformer', mock_transformer):
            entities = extract_entities_from_claim(claim_text)

            # Check entities were extracted correctly
            assert len(entities) == 2
            assert "Company X" in entities
            assert "John Smith" in entities


def test_parse_llm_response():
    """Test parsing JSON response from LLM."""
    # Test valid JSON
    valid_json = '{"verdict": "True", "confidence_score": 85, "reasoning": "Evidence supports claim", "supporting_nodes": ["Node1"]}'
    result = parse_llm_response(valid_json)
    assert result["verdict"] == "True"
    assert result["confidence_score"] == 85

    # Test embedded JSON
    embedded_json = 'Some text before {"verdict": "True", "confidence_score": 85, "reasoning": "Evidence supports claim", "supporting_nodes": ["Node1"]} and after'
    result = parse_llm_response(embedded_json)
    assert result["verdict"] == "True"
    assert result["confidence_score"] == 85

    # Test invalid JSON
    invalid_json = 'Not a JSON at all'
    result = parse_llm_response(invalid_json)
    assert result["verdict"] == "Unknown"
    assert result["confidence_score"] == 0
    assert "Failed to parse" in result["reasoning"]


def test_fact_checker_chain_creation(mock_llm):
    """Test creation of fact checking chain."""
    with patch('src_v3.components.fact_checker.tools.get_bedrock_llm', return_value=mock_llm):
        chain = create_factcheck_chain()
        assert chain is not None


def test_fact_checker_agent_with_articles(mock_llm, test_article, mock_kg):
    """Test the main agent function with GraphState containing articles."""
    # Create the initial state with articles
    test_state = GraphState(
        articles=[test_article],
        current_status="ready"
    )

    # Patch the required functions
    with patch('src_v3.components.fact_checker.fact_checker_Agent.get_bedrock_llm', return_value=mock_llm), \
            patch('src_v3.components.fact_checker.tools.get_bedrock_llm', return_value=mock_llm), \
            patch('src_v3.components.fact_checker.fact_checker_Agent.create_factcheck_chain') as mock_chain, \
            patch('src_v3.components.fact_checker.fact_checker_Agent.extract_entities_from_claim',
                  return_value=["Company X"]):
        # Setup mock chain
        mock_chain.return_value = MagicMock()
        mock_chain.return_value.invoke.return_value = MagicMock(
            content=json.dumps({
                "verdict": "True",
                "confidence_score": 85,
                "reasoning": "Evidence supports claim",
                "supporting_nodes": ["Company X"]
            })
        )

        # Run the agent function
        new_state = fact_checker_agent(test_state, mock_kg)

        # Verify the results
        assert len(new_state.articles) == 1
        assert "fact_check_result" in new_state.articles[0]
        assert new_state.articles[0]["fact_check_result"]["verdict"] == "True"
        assert new_state.current_status == "fact_checked"


def test_fact_checker_agent_with_json_string_articles(mock_llm, test_article, mock_kg):
    """Test handling of articles as JSON strings."""
    # Create article as JSON string
    article_json = json.dumps(test_article)

    # Create the initial state with JSON string article
    test_state = GraphState(
        articles=[article_json],
        current_status="ready"
    )

    # Patch the required functions
    with patch('src_v3.components.fact_checker.fact_checker_Agent.get_bedrock_llm', return_value=mock_llm), \
            patch('src_v3.components.fact_checker.tools.get_bedrock_llm', return_value=mock_llm), \
            patch('src_v3.components.fact_checker.fact_checker_Agent.create_factcheck_chain') as mock_chain, \
            patch('src_v3.components.fact_checker.fact_checker_Agent.extract_entities_from_claim',
                  return_value=["Company X"]):
        # Setup mock chain
        mock_chain.return_value = MagicMock()
        mock_chain.return_value.invoke.return_value = MagicMock(
            content=json.dumps({
                "verdict": "True",
                "confidence_score": 85,
                "reasoning": "Evidence supports claim",
                "supporting_nodes": ["Company X"]
            })
        )

        # Run the agent function
        new_state = fact_checker_agent(test_state, mock_kg)

        # Verify the results
        assert len(new_state.articles) == 1
        assert "fact_check_result" in new_state.articles[0]


def test_fact_checker_agent_error_handling(mock_llm, mock_kg):
    """Test error handling in fact checker agent."""
    # Create an article with no content
    empty_article = {
        'title': 'Empty Article',
        'source': 'Test Source',
        'url': 'https://example.com/empty'
        # No content field
    }

    # Create the initial state
    test_state = GraphState(
        articles=[empty_article],
        current_status="ready"
    )

    # Run the agent function
    new_state = fact_checker_agent(test_state, mock_kg)

    # Verify error was handled
    assert "error" in new_state.articles[0]["fact_check_result"]


def test_fact_checker_agent_exception_handling(mock_llm, test_article, mock_kg):
    """Test exception handling during fact checking."""
    # Create the initial state
    test_state = GraphState(
        articles=[test_article],
        current_status="ready"
    )

    # Patch to raise an exception during fact checking
    with patch('src_v3.components.fact_checker.fact_checker_Agent.extract_entities_from_claim',
               side_effect=Exception("Test exception")):
        # Run the agent function
        new_state = fact_checker_agent(test_state, mock_kg)

        # Verify exception was handled
        assert new_state.articles[0]["fact_check_result"]["verdict"] == "False"
        assert new_state.articles[0]["fact_check_result"]["confidence_score"] == 0
        assert "Error encountered" in new_state.articles[0]["fact_check_result"]["reasoning"]


def test_kg_storage(mock_llm, test_article, mock_kg):
    """Test storing fact check results in knowledge graph."""
    # Create the initial state
    test_state = GraphState(
        articles=[test_article],
        current_status="ready"
    )

    # Patch the required functions
    with patch('src_v3.components.fact_checker.fact_checker_Agent.get_bedrock_llm', return_value=mock_llm), \
            patch('src_v3.components.fact_checker.tools.get_bedrock_llm', return_value=mock_llm), \
            patch('src_v3.components.fact_checker.fact_checker_Agent.create_factcheck_chain') as mock_chain, \
            patch('src_v3.components.fact_checker.fact_checker_Agent.extract_entities_from_claim',
                  return_value=["Company X"]):
        # Setup mock chain
        mock_chain.return_value = MagicMock()
        mock_chain.return_value.invoke.return_value = MagicMock(
            content=json.dumps({
                "verdict": "True",
                "confidence_score": 85,
                "reasoning": "Evidence supports claim",
                "supporting_nodes": ["Company X"]
            })
        )

        # Run the agent function
        fact_checker_agent(test_state, mock_kg)

        # Verify KG storage was called
        mock_kg.add_fact_check_result.assert_called_once()