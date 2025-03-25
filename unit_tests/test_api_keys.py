import os
import pytest
from src.components.news_collector_agent import NewsAPI


def test_news_api_keys():
    """Test if NewsAPI is properly loaded"""
    news_tools = NewsAPI()
    assert news_tools.api_key is not None, "NewsAPI key not loaded"
    assert len(news_tools.api_key) > 0, "NewsAPI key is empty"


def test_news_api_connection():
    """Test if we can actually connect to NEWSAPI"""
    news_tools = NewsAPI()
    articles = news_tools.get_news_article("test")
    assert isinstance(articles, list), "should return list of article"