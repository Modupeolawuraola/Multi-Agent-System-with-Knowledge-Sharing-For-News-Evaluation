import os
import pytest
from unittest.mock import MagicMock, patch
import json
import requests
from datetime import datetime

from src_v2.components.kg_builder.kg_builder import KnowledgeGraph
from langchain_neo4j import Neo4jGraph


@pytest.fixture
def mock_bedrock():
    with patch('boto3.client') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_neo4j():
    with patch('langchain_neo4j.Neo4jGraph') as mock_graph:
        mock_instance = MagicMock()
        # Mock query method
        mock_instance.query.return_value = [
            {"title": "Test Article", "source_name": "Test Source", "url": "https://example.com/test"}
        ]
        mock_graph.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_llm():
    llm = MagicMock()

    # Mock LLM responses
    llm.invoke.return_value = MagicMock(content=json.dumps({
        "entities": [
            {"name": "John Smith", "type": "Person"},
            {"name": "Acme Corp", "type": "Organization"}
        ],
        "relationships": [
            {"source": "John Smith", "target": "Acme Corp", "type": "works_for"}
        ]
    }))

    return llm


@pytest.fixture
def mock_requests():
    with patch('requests.get') as mock_get:
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "totalResults": 2,
            "articles": [
                {
                    "source": {"name": "Test News"},
                    "author": "John Doe",
                    "title": "Test Article 1",
                    "description": "This is test article 1",
                    "url": "https://example.com/article1",
                    "urlToImage": "https://example.com/image1.jpg",
                    "publishedAt": datetime.now().isoformat(),
                    "content": "Test content for article 1"
                },
                {
                    "source": {"name": "Another News"},
                    "author": "Jane Smith",
                    "title": "Test Article 2",
                    "description": "This is test article 2",
                    "url": "https://example.com/article2",
                    "urlToImage": "https://example.com/image2.jpg",
                    "publishedAt": datetime.now().isoformat(),
                    "content": "Test content for article 2"
                }
            ]
        }
        mock_get.return_value = mock_response
        yield mock_get


def test_kg_initialization(mock_neo4j, mock_bedrock):
    """Test that KnowledgeGraph initializes correctly"""
    # Set environment variables for testing
    os.environ["TESTING"] = "true"

    with patch('src_v2.components.kg_builder.kg_builder.ChatBedrock') as mock_bedrock_class:
        mock_bedrock_instance = MagicMock()
        mock_bedrock_class.return_value = mock_bedrock_instance

        # Create KG instance
        kg = KnowledgeGraph()

        # Check that Neo4j was initialized
        assert kg.graph is not None
        assert kg.llm is not None
        assert kg.article_transformer is not None


def test_fetch_news_articles(mock_requests, mock_neo4j, mock_llm):
    """Test fetching articles from NewsAPI"""
    with patch('src_v2.components.kg_builder.kg_builder.ChatBedrock') as mock_bedrock_class:
        mock_bedrock_class.return_value = mock_llm

        # Set NEWS_API_KEY for testing
        os.environ["NEWS_API_KEY"] = "test_api_key"

        # Create KG instance with mocked dependencies
        kg = KnowledgeGraph()

        # Mock add_article to avoid actual processing
        kg.add_article = MagicMock(return_value=True)

        # Test fetch_news_articles
        articles = kg.fetch_news_articles(query="test", days=1, limit=5)

        # Check results
        assert len(articles) == 2
        assert articles[0]['title'] == "Test Article 1"
        assert articles[1]['source'] == "Another News"

        # Check that NewsAPI was called with correct parameters
        mock_requests.assert_called_once()
        args, kwargs = mock_requests.call_args
        assert args[0] == "https://newsapi.org/v2/everything"
        assert kwargs['params']['q'] == "test"
        assert kwargs['params']['pageSize'] == 5

        # Check that add_article was called for each article
        assert kg.add_article.call_count == 2


def test_add_article(mock_neo4j, mock_llm):
    """Test adding an article to the knowledge graph"""
    with patch('src_v2.components.kg_builder.kg_builder.ChatBedrock') as mock_bedrock_class, \
            patch('src_v2.components.kg_builder.kg_builder.LLMGraphTransformer') as mock_transformer_class:
        # Mock LLM and transformer
        mock_bedrock_class.return_value = mock_llm

        mock_transformer = MagicMock()
        mock_transformer.convert_to_graph_documents.return_value = [
            MagicMock(nodes=[MagicMock(id="person1", type="Person")], relationships=[])
        ]
        mock_transformer_class.return_value = mock_transformer

        # Create KG instance
        kg = KnowledgeGraph()

        # Test article
        article = {
            'title': 'Test Article',
            'content': 'This is a test article content.',
            'source': 'Test Source',
            'date': datetime.now().isoformat(),
            'url': 'https://example.com/test'
        }

        # Add article to KG
        result = kg.add_article(article)

        # Check results
        assert result is True

        # Check that Neo4j was queried
        kg.graph.query.assert_called()

        # Check that transformer was used
        mock_transformer.convert_to_graph_documents.assert_called_once()


def test_add_bias_analysis(mock_neo4j, mock_llm):
    """Test adding bias analysis to an article in the knowledge graph"""
    with patch('src_v2.components.kg_builder.kg_builder.ChatBedrock') as mock_bedrock_class:
        mock_bedrock_class.return_value = mock_llm

        # Create KG instance
        kg = KnowledgeGraph()

        # Test article with bias analysis
        article = {
            'title': 'Test Article',
            'content': 'This is a test article content.',
            'source': 'Test Source',
            'date': datetime.now().isoformat(),
            'url': 'https://example.com/test',
            'bias_analysis': {
                'confidence_score': 75,
                'overall_assessment': 'The article shows minimal bias',
                'findings': ['Uses neutral language', 'Presents multiple perspectives']
            }
        }

        # Add bias analysis to KG
        kg.add_bias_analysis(article)

        # Check that Neo4j was queried with correct parameters
        kg.graph.query.assert_called_with(
            """
            MATCH (a:Article {url: $url})
            MERGE (b:BiasAnalysis {article_url: $url})
            SET b.confidence_score = $confidence_score,
                b.overall_assessment = $overall_assessment,
                b.findings = $findings
            MERGE (a)-[:HAS_BIAS_ANALYSIS]->(b)
            """,
            {
                "url": "https://example.com/test",
                "confidence_score": 75,
                "overall_assessment": "The article shows minimal bias",
                "findings": "['Uses neutral language', 'Presents multiple perspectives']"
            }
        )


def test_retrieve_related_articles(mock_neo4j, mock_llm):
    """Test retrieving articles related to a query"""
    with patch('src_v2.components.kg_builder.kg_builder.ChatBedrock') as mock_bedrock_class:
        mock_bedrock_class.return_value = mock_llm

        # Setup mock Neo4j response
        articles = [
            {
                "title": "Related Article 1",
                "source_name": "News Source",
                "url": "https://example.com/article1",
                "published_at": datetime.now().isoformat(),
                "content": "This is related article 1"
            }
        ]
        mock_neo4j.query.return_value = articles

        # Create KG instance
        kg = KnowledgeGraph()

        # Test retrieve_related_articles
        results = kg.retrieve_related_articles(query="test query", limit=3)

        # Check results
        assert len(results) == 1
        assert results[0]['title'] == "Related Article 1"

        # Check that Neo4j was queried with correct parameters
        kg.graph.query.assert_called_with(
            """
            MATCH (a:Article)
            WHERE a.title CONTAINS $query OR a.full_content CONTAINS $query
            RETURN a.title as title, a.source_name as source_name, a.url as url, 
                  a.publishedAt as published_at, a.full_content as content
            LIMIT $limit
            """,
            {
                "query": "test query",
                "limit": 3
            }
        )


def test_get_similar_articles(mock_neo4j, mock_llm):
    """Test retrieving similar articles based on shared entities"""
    with patch('src_v2.components.kg_builder.kg_builder.ChatBedrock') as mock_bedrock_class:
        mock_bedrock_class.return_value = mock_llm

        # Setup mock Neo4j response
        similar_articles = [
            {
                "title": "Similar Article 1",
                "source_name": "News Source",
                "url": "https://example.com/similar1",
                "shared_entities": 3
            }
        ]
        mock_neo4j.query.return_value = similar_articles

        # Create KG instance
        kg = KnowledgeGraph()

        # Test get_similar_articles
        results = kg.get_similar_articles(article_url="https://example.com/test", limit=2)

        # Check results
        assert len(results) == 1
        assert results[0]['title'] == "Similar Article 1"
        assert results[0]['shared_entities'] == 3