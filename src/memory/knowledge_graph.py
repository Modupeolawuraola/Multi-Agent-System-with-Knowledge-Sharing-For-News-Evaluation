import os, json
import torch
import boto3
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from langchain_aws import ChatBedrock
from langchain_community.graphs.graph_document import Node, Relationship

load_dotenv()


class KnowledgeGraph:
    def __init__(self):
        self.graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        # Initialize LLM
        self.llm = self.create_llm()
        # Initialize the article transformer
        self.article_transformer = LLMGraphTransformer(
            llm=self.llm,
            allowed_nodes=[
                "Person", "Organization", "Event", "Policy", "Issue", "Location",
                "Election", "Bill", "Vote", "Speech", "Scandal", "Movement",
                "Alliance", "Media", "Article", "News Source", "Fact Check", "Bias"
            ],
        )

    def create_bedrock_client(self):
        """Create bedrock authenticated Bedrock client"""
        try:
            session = boto3.Session(
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            bedrock_client = session.client(service_name='bedrock-runtime',
                                            region_name=os.getenv('AWS_REGION', 'us-east-1')
                                            )
            return bedrock_client
        except Exception as e:
            print(f"Error creating bedrock client: {e}")
            raise

    def create_llm(self):
        """Create Bedrock LLM Instance"""
        try:
            client = self.create_bedrock_client()
            # initialize anthropic claude model through bedrock
            llm = ChatBedrock(
                client=client,
                model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
                model_kwargs={
                    "max_tokens": 4096,
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            )
            return llm
        except Exception as e:
            print(f"Error initializing Bedrock LLM: {e}")
            raise

    def add_article(self, article):
        """Add a single article to the knowledge graph"""
        source = article.get("source")
        source_name = source["name"] if isinstance(source, dict) else source

        author = article.get("author")
        published_at = article.get("date") or article.get("publishedAt")
        url = article.get("url")
        title = article.get("title")
        full_content = article.get("content") or article.get("full_content")

        # Create a LangChain Document with metadata
        article_doc = [
            Document(
                page_content=full_content or "",
                metadata={
                    "source_name": source_name,
                    "author": author,
                    "publishedAt": published_at,
                    "url": url,
                    "title": title
                }
            )
        ]

        # Convert the article to a graph
        graph_docs = self.article_transformer.convert_to_graph_documents(article_doc)

        # Create the article node
        self.graph.query(
            """
            MERGE (a:Article {url: $url})
            SET a.source_name = $source_name,
                a.author = $author,
                a.publishedAt = $publishedAt,
                a.title = $title,
                a.full_content = $full_content
            """,
            {
                "url": url,
                "source_name": source_name,
                "author": author,
                "publishedAt": published_at,
                "title": title,
                "full_content": full_content
            }
        )

        article_node = Node(
            id=url,
            type="Article"
        )

        # Create relationships between the article node and the generated graph
        for graph_doc in graph_docs:
            for node in graph_doc.nodes:
                graph_doc.relationships.append(
                    Relationship(
                        source=article_node,
                        target=node,
                        type="HAS_ENTITY"
                    )
                )

        # Add the generated nodes and relationships to the graph
        self.graph.add_graph_documents(graph_docs)

        # Add bias analysis if available
        if "bias_analysis" in article:
            self.add_bias_analysis(article)

        # Add fact check if available
        if "fact_check" in article:
            self.add_fact_check(article)

        return True

    def add_bias_analysis(self, article):
        """Add bias analysis data to the knowledge graph"""
        url = article.get("url")
        bias_analysis = article.get("bias_analysis", {})

        self.graph.query(
            """
            MATCH (a:Article {url: $url})
            MERGE (b:BiasAnalysis {article_url: $url})
            SET b.confidence_score = $confidence_score,
                b.overall_assessment = $overall_assessment,
                b.findings = $findings
            MERGE (a)-[:HAS_BIAS_ANALYSIS]->(b)
            """,
            {
                "url": url,
                "confidence_score": bias_analysis.get("confidence_score", 0),
                "overall_assessment": bias_analysis.get("overall_assessment", ""),
                "findings": str(bias_analysis.get("findings", []))
            }
        )

    def add_fact_check(self, article):
        """Add fact check data to the knowledge graph"""
        url = article.get("url")
        fact_check = article.get("fact_check", {})

        self.graph.query(
            """
            MATCH (a:Article {url: $url})
            MERGE (f:FactCheck {article_url: $url})
            SET f.overall_verdict = $overall_verdict,
                f.verified_claims = $verified_claims
            MERGE (a)-[:HAS_FACT_CHECK]->(f)
            """,
            {
                "url": url,
                "overall_verdict": fact_check.get("report", {}).get("overall_verdict", ""),
                "verified_claims": str(fact_check.get("verified_claims", []))
            }
        )

    def create_vector_index(self):
        """Create a vector index for semantic search"""
        self.graph.query("""
            CREATE VECTOR INDEX `chunkVector`
            IF NOT EXISTS
            FOR (c: Chunk) ON (c.textEmbedding)
            OPTIONS {indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
            }};""")

    def retrieve_related_articles(self, query, limit=5):
        """Retrieve articles related to a query"""
        results = self.graph.query(
            """
            MATCH (a:Article)
            WHERE a.title CONTAINS $query OR a.full_content CONTAINS $query
            RETURN a.title, a.source_name, a.url, a.publishedAt
            LIMIT $limit
            """,
            {
                "query": query,
                "limit": limit
            }
        )

        return results

    def add_articles_from_json(self, filename):
        """Add articles from a JSON file to the knowledge graph"""
        with open(filename, encoding="utf-8") as json_file:
            articles_data = json.load(json_file)
        articles = articles_data.get('articles', [])

        for article in articles:
            self.add_article(article)

        # Create vector index after adding articles
        self.create_vector_index()
