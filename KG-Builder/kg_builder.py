import os, json
import torch
import boto3
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from langchain_aws import ChatBedrock
from langchain_openai import ChatOpenAI
from langchain_community.graphs.graph_document import Node, Relationship
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_community.llms import HuggingFacePipeline


env_path = os.path.join('..', '.env')
load_dotenv(env_path)

ARTICLE_FILENAME = 'news_jsons/archive-3-25_3-31/all_articles_3_25-3_31_with_bias.json'
device = "cuda" if torch.cuda.is_available() else "cpu"

def create_bedrock_client():
    """Create bedrock authenticated Bedrock client"""
    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("aws_access_key_id"),
            aws_secret_access_key=os.getenv("aws_secret_access_key"),
            aws_session_token=os.getenv('aws_session_token'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        bedrock_client= session.client(service_name='bedrock-runtime',
                                       region_name=os.getenv('AWS_REGION', 'us-east-1')
                                       )
        return bedrock_client
    except Exception as e:
        print(f"Error creating bedrock client: {e}")
        raise

def create_llm():
    """Create Bedrock LLm Instance"""
    try:
        client = create_bedrock_client()
        #initialize anthropic calude model through bedrock

        llm= ChatBedrock(
            client= client,
            model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_kwargs={
                "max_tokens":4096,
                "temperature":0.2,
                "top_p":0.9
            }
        )
        return llm
    except Exception as e:
        print(f"Error initializing Bedrock LLM: {e}")
        raise




def create_kg():
    with open(ARTICLE_FILENAME, encoding="utf-8") as json_file:
        articles_data = json.load(json_file)
    articles = articles_data.get('articles', [])

    llm = create_llm()

    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )

    article_transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=[
            "Article", "News Source","Bias", "Fact Check",
            "Person", "Organization", "Event", "Policy", "Issue",
            "Location", "Election", "Bill", "Vote", "Speech","Alliance"
        ],
        allowed_relationships=[
            "published_by",  # Article -> News Source
            "has_bias",  # Article -> Bias
            "fact_checked_by",  # Article -> Fact Check
            "mentions",  # Article -> Any other entity (Person, Policy, etc.)

            "affiliated_with",  # Person <-> Organization
            "participated_in",  # Person -> Event
            "endorsed",  # Person -> Policy (or proposed)
            "sponsored",  # Person -> Bill
            "gave_speech",  # Person -> Speech
            "involved_in",  # Person -> Scandal
            "organized",  # Organization -> Event
            "supports",  # Organization -> Policy (or opposes)
            "lobbied_for",  # Organization -> Bill (or lobbied_against)
            "takes_place_in",  # Event -> Location
            "addresses",  # Policy -> Issue (also Speech -> Issue)
            "focuses_on",  # Movement -> Issue
            "decided_by",  # Bill -> Vote
            "includes",  # Alliance -> Organization
            "subject_of"  # Generic: X -> Fact Check
        ]
    )


    for article in articles:
        source = article.get("source")
        source_name = source["name"] if isinstance(source, dict) else source

        author = article.get("author")
        published_at = article.get("publishedAt")
        url = article.get("url")
        title = article.get("title")
        full_content = article.get("full_content")
        content = article.get("content")
        bias = article.get("bias")

        # 5. Create a LangChain Document with minimal necessary metadata
        article_doc = [
            Document(
                page_content=full_content or content,
                metadata={
                    "source_name": source_name,
                    "author": author,
                    "publishedAt": published_at,
                    "url": url,
                    "title": title,
                    "bias": bias

                }
            )
        ]

        # convert the article to a graph
        graph_docs = article_transformer.convert_to_graph_documents(article_doc)

        # create the article node
        graph.query(
            """
            MERGE (a:Article {url: $url})
            SET a.source_name = $source_name,
                a.author = $author,
                a.publishedAt = $publishedAt,
                a.title = $title,
                a.bias = $bias
            """,
            {
                "url": url,
                "source_name": source_name,
                "author": author,
                "publishedAt": published_at,
                "title": title,
                "bias": bias
            }
        )

        article_node = Node(
            id=url,
            type="Article"
        )

        # create relationships between the article node and the generated graph
        for graph_doc in graph_docs:
            for node in graph_doc.nodes:
                graph_doc.relationships.append(
                    Relationship(
                        source=article_node,
                        target=node,
                        type="mentions"
                    )
                )

        # add the generated nodes and relationships to the graph
        graph.add_graph_documents(graph_docs)

    graph.query("""
        CREATE VECTOR INDEX `chunkVector`
        IF NOT EXISTS
        FOR (c: Chunk) ON (c.textEmbedding)
        OPTIONS {indexConfig: {
        `vector.dimensions`: 1536,
        `vector.similarity_function`: 'cosine'
        }};""")


if __name__ == "__main__":
    create_kg()