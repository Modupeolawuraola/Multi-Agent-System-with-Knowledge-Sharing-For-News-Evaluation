import pytest
from src.components.retriever_Agent.retriever_agent import RetrieverAgent
from src.components.updater_agent.updater_agent import UpdaterAgent
from src.memory.schema import GraphState
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_neo4j():
    with patch('langchain_neo4j.Neo4jGraph') as mock_graph:
        mock_instance = MagicMock()
        mock_instance.query.return_value = [{'title': 'Test article'}]
        mock_graph.return_value = mock_instance
        yield mock_instance

def test_retriever(mock_neo4j):
    """Test retriever functionality"""
    initial_state = GraphState(
        knowledge_graph={'articles': [
            {'title': 'Old Article', 'date': (datetime.now() - timedelta(days=2)).isoformat()},
            {'title': 'New Article', 'date': datetime.now().isoformat()},
        ]},
        last_retrieved_date=(datetime.now() - timedelta(days=1)).isoformat()
    )

    new_state = RetrieverAgent(initial_state)

    assert len(new_state.retrieved_articles) == 1
    assert new_state.current_status == 'retrieval_complete'


def test_updater(mock_neo4j):
    """Test updater functionality"""
    with patch('src.components.updater_agent.updater_agent.KnowledgeGraph') as mock_kg_class:
        # Setup mock KG instance
        mock_kg = MagicMock()
        mock_kg_class.return_value = mock_kg

        # Configure add_article to do something observable
        mock_kg.add_article.side_effect = lambda article: article

        # Test state with articles to add
        initial_state = GraphState(
            knowledge_graph={'articles': []},
            articles=[{'title': 'New Article'}],  # Note: using articles, not retrieved_articles
            current_status='retrieval_complete'
        )

        # Run updater
        new_state = UpdaterAgent(initial_state)

        # Verify updater called add_article
        assert mock_kg.add_article.call_count == 1
        assert new_state.current_status == 'update_complete'
