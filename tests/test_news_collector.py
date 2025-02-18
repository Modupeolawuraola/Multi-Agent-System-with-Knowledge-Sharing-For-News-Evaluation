import pytest
from src.components.news_collector_agent import NewsAPI
from src.components.news_collector_agent import new_collector_Agent
from src.memory.schema import GraphState

def test_news_collector_init():
    """Test if news collector initializes properly"""
    tool =NewsAPI()
    assert tool.api_key is not None

def test_news_collector_get_articles():
    """Test if news collector gets articles"""
    tool =NewsAPI()
    articles =tool.get_news_article("test")
    assert isinstance(articles, list)
    if len(articles) > 0:
        assert 'title' in articles[0]
        assert 'content' in articles[0]

def test_news_collector_Agent():
    """Test if the node/agent works properly"""
    initial_state =GraphState(
        knowledge_graph={},
        article=[],
        current_status="ready"
    )

    new_state=new_collector_Agent(initial_state)
    assert new_state['current_status'] == "collection_complete"
    assert isinstance(new_state['articles'], list)
