import os, json
import logging
import boto3
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from langchain_aws import ChatBedrock
from langchain_community.graphs.graph_document import Node, Relationship
import requests
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()


class KnowledgeGraph:
    def __init__(self):
        """Initialize the Knowledge Graph with Neo4j connection"""
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

    def fetch_news_articles(self, query="politics", days=1, limit=10):
        """
        Fetch articles directly from NewsAPI
        Replaces the news collector agent functionality
        """
        api_key = os.environ.get('NEWS_API_KEY')
        if not api_key:
            raise ValueError("NEWS_API_KEY environment variable is not set")

        base_url = "https://newsapi.org/v2/everything"
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'publishedAt',
            'apiKey': api_key,
            'language': 'en',
            'pageSize': limit
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            articles = response.json()['articles']

            # Format articles to match schema
            formatted_articles = []
            for article in articles:
                formatted_article = {
                    'title': article.get('title'),
                    'content': article.get('content'),
                    'source': article.get('source', {}).get('name'),
                    'date': article.get('publishedAt'),
                    'url': article.get('url')
                }
                formatted_articles.append(formatted_article)

                # Immediately add each article to the KG
                self.add_article(formatted_article)

            return formatted_articles
        except Exception as e:
            print(f"Error fetching news articles: {e}")
            return []

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
            RETURN a.title as title, a.source_name as source_name, a.url as url, 
                  a.publishedAt as published_at, a.full_content as content
            LIMIT $limit
            """,
            {
                "query": query,
                "limit": limit
            }
        )

        # Convert the results to a list of dictionaries
        articles = [dict(record) for record in results]
        return articles

    def add_articles_from_json(self, filename):
        """Add articles from a JSON file to the knowledge graph"""
        with open(filename, encoding="utf-8") as json_file:
            articles_data = json.load(json_file)
        articles = articles_data.get('articles', [])

        for article in articles:
            self.add_article(article)

        # Create vector index after adding articles
        self.create_vector_index()

    def get_similar_articles(self, article_url, limit=3):
        """Find similar articles based on shared entities"""
        results = self.graph.query(
            """
            MATCH (a:Article {url: $url})-[:HAS_ENTITY]->(e)
            MATCH (e)<-[:HAS_ENTITY]-(similar:Article)
            WHERE similar.url <> $url
            RETURN similar.title as title, similar.source_name as source_name, 
                   similar.url as url, COUNT(e) as shared_entities
            ORDER BY shared_entities DESC
            LIMIT $limit
            """,
            {
                "url": article_url,
                "limit": limit
            }
        )

        return [dict(record) for record in results]

    def get_bias_report(self, topic, limit=10):
        """
        Generate a report of bias across news sources on a specific topic
        """
        results = self.graph.query(
            """
            MATCH (a:Article)-[:HAS_BIAS_ANALYSIS]->(b:BiasAnalysis)
            WHERE a.title CONTAINS $topic OR a.full_content CONTAINS $topic
            RETURN a.source_name as source, b.overall_assessment as assessment,
                   COUNT(a) as article_count
            GROUP BY a.source_name, b.overall_assessment
            ORDER BY article_count DESC
            LIMIT $limit
            """,
            {
                "topic": topic,
                "limit": limit
            }
        )

        return [dict(record) for record in results]

    def get_similar_articles_by_embedding(self, article_url: str, top_k: int = 5) -> list:
        """Find top-k articles most similar to the given article using Node2Vec embeddings."""
        # Get target embedding
        query = """
        MATCH (a:Article {url: $url}) 
        RETURN id(a) AS id, a.node2vecEmbedding AS embedding
        """
        result = self.graph.query(query, {"url": article_url})
        if not result or not result[0].get("embedding"):
            return []

        target_embedding = np.array(result[0]["embedding"]).reshape(1, -1)

        # Get all candidate articles with embeddings
        query = """
        MATCH (b:Article)
        WHERE exists(b.node2vecEmbedding) AND b.url <> $url AND exists((b)-[:HAS_BIAS]->(:Bias))
        RETURN b.title AS title, b.url AS url, b.node2vecEmbedding AS embedding,
               [(b)-[:HAS_BIAS]->(bias:Bias) | bias.label][0] AS bias
        """
        candidates = self.graph.query(query, {"url": article_url})

        # Compute similarity scores
        scored = []
        for c in candidates:
            embedding = np.array(c["embedding"]).reshape(1, -1)
            sim_score = cosine_similarity(target_embedding, embedding)[0][0]
            scored.append({
                "title": c["title"],
                "url": c["url"],
                "bias": c["bias"],
                "similarity": sim_score
            })

        return sorted(scored, key=lambda x: x["similarity"], reverse=True)[:top_k]

    def query_most_structurally_similar_bias(self, entities: list) -> str:
        """
        Finds the single most structurally similar article based on shared entities and returns its bias.
        """
        if not entities:
            return "Unknown"

        escaped = [f'"{e.replace("\"", "")}"' for e in entities]
        entity_list = f"[{', '.join(escaped)}]"

        cypher = f"""
        MATCH (e)
        WHERE e.id IN {entity_list}

        MATCH (e)<-[:MENTIONS]-(a:Article)
        WHERE a.bias IS NOT NULL

        WITH a, a.bias AS bias, count(*) AS overlap_score
        ORDER BY overlap_score DESC
        RETURN a.title AS title, bias
        LIMIT 1
        """

        try:
            results = self.graph.query(cypher)
            if results:
                logging.info(f"Most similar article from KG: {results[0]['title']} with bias {results[0]['bias']}")
                return results[0]["bias"].capitalize()
        except Exception as e:
            logging.error(f"[KG query error] {e}")

        return "Unknown"