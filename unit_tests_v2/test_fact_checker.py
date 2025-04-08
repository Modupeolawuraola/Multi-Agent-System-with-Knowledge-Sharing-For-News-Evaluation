import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import modules to test
from src_v2.components.fact_checker.fact_checker_Agent import FactCheckerAgent, fact_checker_agent
from src_v2.components.fact_checker.tools import FactCheckTools
from src_v2.memory.schema import GraphState
from src_v2.components.kg_builder.kg_builder import KnowledgeGraph


@pytest.fixture
def mock_bedrock():
    with patch('boto3.client') as mock_client:
        # Setup mock client behavior
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance


# Use pytest fixtures instead of setUp
@pytest.fixture
def mock_llm():
    llm = MagicMock()

    # Set up different responses based on the input
    def side_effect(input_data):
        # If looking for claims extraction
        if isinstance(input_data, list) and len(input_data) >= 2 and "Extract the key factual claims" in input_data[
            0].get("content", ""):
            return MagicMock(
                content=json.dumps({
                    "claims": [
                        {
                            "claim": "Company X reported 20% growth in Q3",
                            "entities": ["Company X"],
                            "category": "statistical",
                            "importance": 8
                        },
                        {
                            "claim": "CEO John Smith said the company plans to expand to Europe next year",
                            "entities": ["John Smith", "Company X", "Europe"],
                            "category": "quotation",
                            "importance": 7
                        }
                    ]
                })
            )
        # If looking for verification
        elif isinstance(input_data, list) and len(
                input_data) >= 2 and "assess whether the provided evidence confirms" in input_data[0].get("content",
                                                                                                          ""):
            return MagicMock(
                content=json.dumps({
                    "is_verified": True,
                    "confidence": 0.85,
                    "verdict": "confirmed",
                    "reasoning": "Multiple reliable sources confirm the claim.",
                    "evidence_quality": 0.8,
                    "evidence_reliability": 0.9,
                    "contradicting_evidence": "",
                    "corroborating_sources": ["Financial Times", "Bloomberg"]
                })
            )
        # If looking for overall report
        elif isinstance(input_data, list) and len(
                input_data) >= 2 and "provide an overall assessment of the article's factual accuracy" in input_data[
            0].get("content", ""):
            return MagicMock(
                content=json.dumps({
                    "overall_accuracy": 0.9,
                    "overall_verdict": "highly accurate",
                    "reasoning": "The key claims in the article are supported by evidence.",
                    "key_issues": [],
                    "strongest_claims": ["Company X reported 20% growth in Q3"],
                    "weakest_claims": [],
                    "missing_context": "",
                    "source_credibility": 0.85,
                    "evidence_strength": 0.9,
                    "recommendations": "The article is generally reliable."
                })
            )
        else:
            return MagicMock(content="{}")

    llm.invoke.side_effect = side_effect
    return llm


@pytest.fixture
def mock_kg():
    """Mock KnowledgeGraph for testing"""
    mock = MagicMock(spec=KnowledgeGraph)

    # Mock KG methods
    mock.retrieve_related_articles.return_value = [
        {
            "title": "Company X Quarterly Report",
            "source_name": "Financial Times",
            "url": "https://example.com/company-x-q3",
            "published_at": "2025-02-15T10:00:00Z",
            "content": "Company X reported 20% growth in Q3. CEO John Smith announced plans to expand to Europe."
        }
    ]

    mock.add_fact_check.return_value = True

    return mock


@pytest.fixture
def fact_checker(mock_llm):
    return FactCheckerAgent(mock_llm, kg=None)


@pytest.fixture
def test_article():
    return {
        'title': 'Company X Reports Strong Growth',
        'content': 'Company X reported 20% growth in Q3. CEO John Smith said the company plans to expand to Europe next year.',
        'source': 'Business News Daily',
        'date': '2025-02-15T12:00:00Z',
        'url': 'https://example.com/business-news'
    }


def test_extract_claims(fact_checker, test_article):
    """Test claim extraction from article."""
    claims = fact_checker.extract_claims(test_article)

    # Check that claims were extracted correctly
    assert len(claims) == 2
    assert claims[0]['claim'] == 'Company X reported 20% growth in Q3'
    assert claims[1]['category'] == 'quotation'

    # Check for entities in claims (new field)
    assert 'entities' in claims[0]
    assert 'Company X' in claims[0]['entities']


def test_verify_claim_with_evidence(fact_checker, mock_llm):
    """Test the new verify_claim_with_evidence method."""
    claim_text = "Company X reported 20% growth in Q3"
    evidence = [
        {
            "source": "web_search",
            "title": "Company X Q3 Results",
            "content": "Company X announced a 20% increase in revenue for Q3.",
            "url": "https://example.com/company-x-q3",
            "source_name": "Financial Times",
            "source_credibility": 0.9,
            "source_type": "news_outlet"
        }
    ]

    verification = fact_checker.verify_claim_with_evidence(claim_text, evidence)

    # Check verification results
    assert verification['is_verified'] is True
    assert verification['confidence'] >= 0.8
    assert verification['verdict'] == 'confirmed'
    assert 'evidence_quality' in verification
    assert 'evidence_reliability' in verification
    assert 'corroborating_sources' in verification


def test_verify_claims(fact_checker, mock_llm, test_article):
    """Test claim verification with evidence."""
    # Mock evidence search result
    with patch('src_v2.components.fact_checker.tools.FactCheckTools.search_for_evidence') as mock_search:
        mock_search.return_value = [
            {
                "source": "web_search",
                "title": "Company X Q3 Results",
                "content": "Company X announced a 20% increase in revenue for Q3.",
                "url": "https://example.com/company-x-q3",
                "source_name": "Financial Times",
                "source_credibility": 0.9,
                "source_type": "news_outlet"
            }
        ]

        # Test claims
        claims = [
            {
                "claim": "Company X reported 20% growth in Q3",
                "entities": ["Company X"],
                "category": "statistical",
                "importance": 8
            }
        ]

        verified_claims = fact_checker.verify_claims(claims)

        # Check verification results
        assert len(verified_claims) == 1
        assert verified_claims[0]['verification']['is_verified'] is True
        assert verified_claims[0]['verification']['confidence'] >= 0.8
        assert 'entities' in verified_claims[0]


def test_generate_fact_check_report(fact_checker, mock_llm, test_article):
    """Test generating overall report."""
    # Test with verified claims
    verified_claims = [
        {
            "claim": "Company X reported 20% growth in Q3",
            "entities": ["Company X"],
            "evidence": [{"source": "web_search", "content": "Company X announced 20% growth"}],
            "verification": {
                "is_verified": True,
                "confidence": 0.9,
                "verdict": "confirmed",
                "evidence_quality": 0.8,
                "evidence_reliability": 0.85
            }
        }
    ]

    report = fact_checker.generate_fact_check_report(test_article, verified_claims)

    # Check report
    assert report['overall_accuracy'] >= 0.8
    assert report['overall_verdict'] == 'highly accurate'
    assert 'source_credibility' in report
    assert 'evidence_strength' in report


def test_fact_checker_agent_function_with_articles(mock_llm, mock_bedrock, test_article, mock_kg):
    """Test the main agent function with GraphState containing articles."""
    with patch('src_v2.components.fact_checker.fact_checker.FactCheckerAgent') as mock_agent_class:
        # Setup mock agent instance
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Mock agent methods
        mock_agent.extract_claims.return_value = [{"claim": "Test claim", "entities": ["Test entity"]}]
        mock_agent.verify_claims.return_value = [{"claim": "Test claim", "verification": {"is_verified": True}}]
        mock_agent.generate_fact_check_report.return_value = {"overall_accuracy": 0.8}

        # Test state
        test_state = GraphState(
            articles=[test_article],
            current_status="ready"
        )

        # Run agent function
        new_state = fact_checker_agent(test_state, mock_kg)

        # Check state was updated
        assert new_state.current_status == 'fact_check_complete'
        assert 'fact_check' in new_state.articles[0]
        assert 'report' in new_state.articles[0]['fact_check']

        # Check that KG methods were called
        mock_kg.add_fact_check.assert_called_once()


def test_fact_checker_agent_function_with_query(mock_llm, mock_kg):
    """Test the main agent function with a direct news query."""
    with patch('src_v2.components.fact_checker.fact_checker.FactCheckerAgent') as mock_agent_class, \
            patch('src_v2.components.fact_checker.fact_checker.FactCheckerAgent.extract_claims') as mock_extract, \
            patch('src_v2.components.fact_checker.fact_checker.FactCheckerAgent.verify_claims') as mock_verify, \
            patch(
                'src_v2.components.fact_checker.fact_checker.FactCheckerAgent.generate_fact_check_report') as mock_report:
        # Setup mock agent instance and methods
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        mock_extract.return_value = [{"claim": "President said X", "entities": ["President"]}]
        mock_verify.return_value = [{"claim": "President said X", "verification": {"is_verified": False}}]
        mock_report.return_value = {"overall_accuracy": 0.3, "overall_verdict": "inaccurate"}

        # Test state with news query
        test_state = GraphState(
            news_query='President said the economy is booming',
            current_status="ready"
        )

        # Run agent function
        new_state = fact_checker_agent(test_state, mock_kg)

        # Check state was updated with fact check result
        assert new_state.current_status == 'fact_check_complete'
        assert new_state.fact_check_result is not None
        assert 'status' in new_state.fact_check_result
        assert 'verified_claims' in new_state.fact_check_result
        assert 'report' in new_state.fact_check_result


def test_fact_checker_agent_knowledge_graph_match(mock_kg, mock_llm):
    """Test finding matches in the knowledge graph."""
    # Configure mock KG to return matching articles
    matching_article = {
        'title': 'Test News About Topic X',
        'content': 'This is a test article about Topic X with important facts.',
        'source_name': 'Test Source',
        'url': 'https://example.com/test-article'
    }
    mock_kg.retrieve_related_articles.return_value = [matching_article]

    # Create the initial state
    test_state = GraphState(
        news_query='Tell me about Topic X facts',
        current_status="ready"
    )

    # Set up mocks
    with patch('src_v2.utils.aws_helpers.get_bedrock_llm', return_value=mock_llm), \
            patch('src_v2.components.fact_checker.fact_checker.FactCheckerAgent.extract_claims',
                  return_value=[{"claim": "Test claim"}]), \
            patch('src_v2.components.fact_checker.fact_checker.FactCheckerAgent.verify_claims',
                  return_value=[{"claim": "Test claim", "verification": {"is_verified": True}}]), \
            patch('src_v2.components.fact_checker.fact_checker.FactCheckerAgent.generate_fact_check_report',
                  return_value={"overall_accuracy": 0.9}):
        # Run the agent
        new_state = fact_checker_agent(test_state, mock_kg)

        # Check that KG match was found
        assert new_state.fact_check_result is not None
        assert 'matched_articles' in new_state.fact_check_result
        assert len(new_state.fact_check_result['matched_articles']) > 0
        assert new_state.fact_check_result['matched_knowledge_graph'] is True

        # Check that KG was queried
        mock_kg.retrieve_related_articles.assert_called_once()