import os
import pytest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime

from src_v3.components.kg_builder.kg_builder import KnowledgeGraph
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

    with patch('src_v3.components.kg_builder.kg_builder.ChatBedrock') as mock_bedrock_class, \
            patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.create_bedrock_client') as mock_create_client:
        mock_bedrock_instance = MagicMock()
        mock_bedrock_class.return_value = mock_bedrock_instance
        mock_create_client.return_value = MagicMock()

        # Create KG instance
        kg = KnowledgeGraph()

        # Check that Neo4j was initialized
        assert kg.graph is not None
        assert kg.llm is not None
        assert kg.article_transformer is not None


def test_fetch_news_articles(mock_requests, mock_neo4j, mock_llm):
    """Test fetching articles from NewsAPI"""
    with patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.create_llm', return_value=mock_llm), \
            patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.add_article', return_value=True):
        # Set NEWS_API_KEY for testing
        os.environ["NEWS_API_KEY"] = "test_api_key"

        # Create KG instance with mocked dependencies
        kg = KnowledgeGraph()
        kg.llm = mock_llm

        # Test fetch_news_articles
        articles = kg.fetch_news_articles(query="test", days=1, limit=5)

        # Check results
        assert len(articles) == 2
        assert articles[0]['title'] == 'Test Article 1'
        assert articles[1]['title'] == 'Test Article 2'


def test_add_article(mock_neo4j, mock_llm):
    """Test adding an article to the knowledge graph"""
    with patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.create_llm', return_value=mock_llm), \
            patch('src_v3.components.kg_builder.kg_builder.LLMGraphTransformer'):
        # Create KG instance
        kg = KnowledgeGraph()
        kg.llm = mock_llm
        kg.graph = mock_neo4j

        # Test article
        article = {
            'title': 'Test Article',
            'content': 'This is a test article content.',
            'source': 'Test Source',
            'date': datetime.now().isoformat(),
            'url': 'https://example.com/test'
        }

        # Test adding article
        result = kg.add_article(article)

        # Verify result and that query was called
        assert result is True
        assert mock_neo4j.query.call_count > 0


def test_add_bias_analysis(mock_neo4j, mock_llm):
    """Test adding bias analysis to an article in the knowledge graph"""
    with patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.create_llm', return_value=mock_llm):
        # Create KG instance
        kg = KnowledgeGraph()
        kg.llm = mock_llm
        kg.graph = mock_neo4j

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

        # Check that Neo4j query was called
        assert mock_neo4j.query.call_count > 0


def test_add_fact_check_result(mock_neo4j, mock_llm):
    """Test adding fact check results to the knowledge graph"""
    with patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.create_llm', return_value=mock_llm):
        # Create KG instance
        kg = KnowledgeGraph()
        kg.llm = mock_llm
        kg.graph = mock_neo4j

        # Test fact check result
        claim = "Company X reported 20% growth in Q3"
        result = {
            "verdict": "True",
            "confidence_score": 85,
            "reasoning": "Multiple reliable sources confirm the claim."
        }
        related_entities = ["Company X", "Q3 2025"]

        # Add fact check to KG
        success = kg.add_fact_check_result(claim, result, related_entities)

        # Check that Neo4j query was called
        assert success is True
        assert mock_neo4j.query.call_count > 0


def test_add_articles_from_json(mock_neo4j, mock_llm, tmp_path):
    """Test adding articles from a JSON file"""
    with patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.create_llm', return_value=mock_llm):
        # Create a temporary JSON file with test articles
        test_articles = {
            "articles": [
                {
                    "title": "Test Article 1",
                    "content": "Test content 1",
                    "source": "Test Source 1",
                    "url": "https://example.com/test1"
                },
                {
                    "title": "Test Article 2",
                    "content": "Test content 2",
                    "source": "Test Source 2",
                    "url": "https://example.com/test2"
                }
            ]
        }

        json_file = tmp_path / "test_articles.json"
        with open(json_file, 'w') as f:
            json.dump(test_articles, f)

        # Create KG instance
        kg = KnowledgeGraph()
        kg.llm = mock_llm
        kg.graph = mock_neo4j

        # Mock add_article method
        kg.add_article = MagicMock(return_value=True)
        kg.create_vector_index = MagicMock()

        # Test adding articles from JSON
        kg.add_articles_from_json(str(json_file))

        # Verify correct number of articles were added
        assert kg.add_article.call_count == 2
        # Verify vector index was created
        assert kg.create_vector_index.call_count == 1


def test_retrieve_related_articles(mock_neo4j, mock_llm):
    """Test retrieving articles related to a query"""
    with patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.create_llm', return_value=mock_llm):
        # Create KG instance
        kg = KnowledgeGraph()
        kg.llm = mock_llm
        kg.graph = mock_neo4j

        # Set up mock return value for query
        mock_neo4j.query.return_value = [
            {
                "title": "Test Article 1",
                "source_name": "Test Source 1",
                "url": "https://example.com/test1",
                "published_at": datetime.now().isoformat(),
                "content": "Test content 1"
            },
            {
                "title": "Test Article 2",
                "source_name": "Test Source 2",
                "url": "https://example.com/test2",
                "published_at": datetime.now().isoformat(),
                "content": "Test content 2"
            }
        ]

        # Test retrieving related articles
        articles = kg.retrieve_related_articles("test query", limit=2)

        # Verify results
        assert len(articles) == 2
        assert articles[0]["title"] == "Test Article 1"
        assert articles[1]["title"] == "Test Article 2"


def test_query_most_structurally_similar_bias(mock_neo4j, mock_llm):
    """Test querying for most structurally similar bias"""
    with patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.create_llm', return_value=mock_llm):
        # Create KG instance
        kg = KnowledgeGraph()
        kg.llm = mock_llm
        kg.graph = mock_neo4j

        # Set up mock return value for query
        mock_neo4j.query.return_value = [
            {
                "title": "Similar Article",
                "bias": "center"
            }
        ]

        # Test entities
        entities = ["Company X", "John Smith"]

        # Get most structurally similar bias
        bias = kg.query_most_structurally_similar_bias(entities)

        # Verify result
        assert bias == "Center"  # Should be capitalized as per the implementation


def test_retrieve_related_facts_text(mock_neo4j, mock_llm):
    """Test retrieving related facts as text"""
    with patch('src_v3.components.kg_builder.kg_builder.KnowledgeGraph.create_llm', return_value=mock_llm):
        # Create KG instance
        kg = KnowledgeGraph()
        kg.llm = mock_llm
        kg.graph = mock_neo4j

        # Set up mock return value for query
        mock_neo4j.query.return_value = [
            {
                "source_node": "Company X",
                "source_labels": ["Entity", "Organization"],
                "relationship": "MENTIONS",
                "target_node": "John Smith",
                "target_labels": ["Entity", "Person"]
            },
            {
                "source_node": "John Smith",
                "source_labels": ["Entity", "Person"],
                "relationship": "WORKS_FOR",
                "target_node": "Company X",
                "target_labels": ["Entity", "Organization"]
            }
        ]

        # Test entities
        entities = ["Company X", "John Smith"]

        # Get related facts
        facts = kg.retrieve_related_facts_text(entities)

        # Verify that facts are returned as a string
        assert isinstance(facts, str)
        assert len(facts) > 0