import os
import pytest
import requests
from src_v2.components.kg_builder.kg_builder import KnowledgeGraph


def test_news_api_keys():
    """Test if NewsAPI key is properly loaded"""
    news_api_key = os.environ.get('NEWS_API_KEY')
    assert news_api_key is not None, "NewsAPI key not loaded"
    assert len(news_api_key) > 0, "NewsAPI key is empty"


def test_news_api_connection():
    """Test if we can actually connect to NewsAPI via KnowledgeGraph"""
    # Create the KG class
    kg = KnowledgeGraph()

    # Test the fetch_news_articles method
    articles = kg.fetch_news_articles("test", days=1, limit=3)

    # Check results
    assert isinstance(articles, list), "should return list of articles"

    # Make a basic direct API call as a backup test
    news_api_key = os.environ.get('NEWS_API_KEY')
    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            'q': 'test',
            'apiKey': news_api_key,
            'pageSize': 1
        }
    )
    assert response.status_code == 200, "NewsAPI connection failed"