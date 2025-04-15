from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
from src_v3.utils.aws_helpers import get_aws_credentials, diagnostic_check
from typing import List
from langchain_neo4j import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
import logging
from .b_prompts import (
    BiasAnalysisSimplifiedPrompt
)
from dotenv import load_dotenv
import boto3
import os
load_dotenv()


def create_bedrock_client():
    """Create authenticated Bedrock client"""
    try:
        # Get credentials using our helper function
        credentials = get_aws_credentials()

        # Print debug info without revealing secrets
        if credentials['aws_access_key_id']:
            print(
                f"Using access key ID: {credentials['aws_access_key_id'][:4]}...{credentials['aws_access_key_id'][-4:]}")
        else:
            print("WARNING: AWS_ACCESS_KEY_ID not found in environment")

        print(f"Using AWS region: {credentials['region_name']}")

        # Create session
        session = boto3.Session(**credentials)

        # Create client
        bedrock_client = session.client(service_name='bedrock-runtime')

        return bedrock_client
    except Exception as e:
        print(f"Error creating bedrock client: {e}")
        print(f"Current working directory: {os.getcwd()}")
        raise


def create_llm():
    """Create Bedrock LLM Instance"""
    try:
        # Always use real AWS Bedrock - no mocks
        print("Using real AWS Bedrock")
        client = create_bedrock_client()
        llm = ChatBedrock(
            client=client,
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", #anthropic.claude-3-sonnet-20240229-v1:0
            model_kwargs={
                "max_tokens": 4096,
                "temperature": 0.2,
                "top_p": 0.9
            }
        )
        return llm
    except Exception as e:
        print(f"Error initializing Bedrock LLM: {e}")
        raise  # raise error if AWS fails


def create_bias_analysis_chain():
    """Create the bias analysis chain"""
    try:
        # Always use real AWS Bedrock LLM - no mocks
        client = create_bedrock_client()
        llm = ChatBedrock(
            client=client,
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_kwargs={
                "max_tokens": 4096,
                "temperature": 0.2,
                "top_p": 0.9
            }
        )

        chain = (
                RunnablePassthrough() |
                BiasAnalysisSimplifiedPrompt |
                llm
        )

        return chain

    except Exception as e:
        print(f"Error creating bias analysis chain: {e}")
        raise

def format_article(article: dict) -> dict:
    """Formats article for analysis"""
    title = article.get('title') or article.get('headline') or 'Untitled'
    content = article.get('full_content') or article.get('content') or ''
    source = article.get('source') or article.get('source_name') or 'Unknown Source'
    date = article.get('date') or article.get('publishedAt') or 'No date provided'

    formatted_text = f"""
    Title: {title}
    Content: {content}
    Source: {source}
    Date: {date}
    """.strip()

    # return dictionary with the formatted text
    return formatted_text
transformer = None

def initialize_entity_extractor(llm) -> None:
    """Initialize the LLMGraphTransformer for entity extraction"""
    global transformer
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=[
            "Person", "Organization", "Event", "Policy", "Issue", "Location",
            "Election", "Bill", "Vote", "Speech", "Alliance"
        ],
        allowed_relationships=[
            "published_by", "has_bias","fact_checked_by", "mentions",
            "affiliated_with", "participated_in", "endorsed",  "sponsored",
            "gave_speech", "involved_in", "organized",  "supports",
            "lobbied_for", "takes_place_in", "addresses",  "focuses_on",
            "decided_by", "includes", "subject_of"
        ]
    )

def extract_entities(article: str) -> List[str]:
    """Extracts named entities from article content using LLM-based graph transformation."""
    logging.info(f"Extracting from article: {article.get('title', '')}")
    logging.info(f"Article content length: {len(article.get('full_content', ''))}")
    global transformer
    if transformer is None:
        raise RuntimeError("Transformer not initialized. Call initialize_entity_extractor(llm) first.")

    doc = Document(
        page_content=article.get("full_content", ""),
        metadata={
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "date": article.get("date", ""),
            "url": article.get("url", "")
        }
    )
    graph_objs = transformer.convert_to_graph_documents([doc])
    entities = []
    for graph in graph_objs:
        # logging.info(f"GraphDoc Nodes: {graph.nodes}")
        for node in graph.nodes:
            name = node.properties.get("name") or node.id
            if name:
                entities.append(name)

    entities = list(set([e.strip() for e in entities if e.strip()]))
    logging.info(f"Extracted entities: {entities}")
    return list(set(entities))

def get_similar_articles(article_content: str, graph: Neo4jGraph, top_k: int = 3) -> List[str]:
    """
    Query the KG for articles that share entities with the input article content.
    Returns up to `top_k` article texts.
    """
    # Step 1: Extract entities (e.g., Person, Organization, Policy)
    entities = extract_entities(article_content)
    if not entities:
        return []

    # Sanitize for Cypher
    entity_names = [e.replace("'", "\\'") for e in entities]

    # Step 2: Cypher query to find similar articles
    cypher = f"""
    MATCH (e)<-[:mentions]-(a:Article)
    WHERE e.name IN {entity_names}
    WITH a, count(*) AS overlap
    ORDER BY overlap DESC
    RETURN a.full_content AS content
    LIMIT {top_k}
    """

    try:
        results = graph.query(cypher)
        return [record['content'] for record in results if record.get('content')]
    except Exception as e:
        print(f"[KG Query Error] {e}")
        return []

def format_similar_articles(similar_context: list) -> str:
    if not similar_context:
        return "No similar articles found in the knowledge graph."
    return "\n".join(
        f"- {a['title']} | Bias: {a['bias']} | Similarity Score: {round(a['similarity'], 2)}"
        for a in similar_context
    )