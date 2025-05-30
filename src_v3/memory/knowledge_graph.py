import os, json
from typing import List, Dict, Any
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

    def add_bias_analysis(self, article_url: str, bias_analysis: Dict) -> bool:
        """Add bias analysis results to an article.

        Args:
            article_url (str): URL of the article
            bias_analysis (Dict): Bias analysis results

        Returns:
            bool: Success status
        """
        try:
            # Extract bias properties
            overall = bias_analysis.get('bias', 'Neutral')
            score = bias_analysis.get('confidence_score', 50)
            reasoning = bias_analysis.get('reasoning', '')

            # Create bias node and connect to article
            self.graph.query(
                """
                MATCH (a:Article {url: $url})
                MERGE (b:Bias {id: $url + "_bias"})
                SET b.overall_assessment = $overall,
                    b.confidence_score = $score,
                    b.reasoning = $reasoning,
                    b.timestamp = $timestamp
                MERGE (a)-[:has_bias]->(b)
                """,
                {
                    'url': article_url,
                    'overall': overall,
                    'score': score,
                    'reasoning': reasoning,
                    'timestamp': datetime.now().isoformat()
                }
            )

            logging.info(f"Added bias analysis for article: {article_url}")
            return True

        except Exception as e:
            logging.error(f"Error adding bias analysis: {e}")
            return False

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
        """Get a report of bias across news sources on a topic.

        Args:
            topic (str): Topic to analyze bias for
            limit (int): Maximum number of sources to include

        Returns:
            List of dictionaries with source name and bias assessment
        """
        try:
            # Escape the topic for search
            search_topic = topic.replace("'", "\\'")

            results = self.graph.query(
                f"""
                MATCH (a:Article)-[:has_bias]->(b:Bias)
                WHERE a.title CONTAINS '{search_topic}' OR a.content CONTAINS '{search_topic}'
                WITH a.source_name as source, b.overall_assessment as assessment, count(*) as article_count
                RETURN source, assessment, article_count
                ORDER BY article_count DESC
                LIMIT {limit}
                """
            )

            bias_report = []
            for record in results:
                source = record.get('source', 'Unknown Source')
                assessment = record.get('assessment', 'Neutral')
                count = record.get('article_count', 0)

                bias_report.append({
                    'source': source,
                    'assessment': assessment,
                    'article_count': count
                })

            return bias_report

        except Exception as e:
            logging.error(f"Error getting bias report: {e}")
            return []

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
            return ""

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

    def retrieve_related_facts_text(self, entities: List[str], limit: int = 25) -> str:
        """
        Retrieve relationship-level context from the KG for the given entities.
        Returns a human-readable string summary.
        """
        if not self.graph:
            logging.warning("[KG] Knowledge graph is not available.")
            return ""

        if not entities:
            logging.warning("[KG] No entities provided for context retrieval.")
            return ""

        logging.info(f"[KG] Retrieving context for entities: {entities}")
        query = """
        MATCH (e)
        WHERE e.id IN $entities
        OPTIONAL MATCH (n1)-[r2]-(n2)

        MATCH (e)-[r]-(n)
        RETURN DISTINCT
          e.id AS source_node,
          labels(e) AS source_labels,
          type(r) AS relationship,
          n.id AS target_node,
          labels(n) AS target_labels
        LIMIT $limit
        """

        try:
            records = self.graph.query(query, params={"entities": entities, "limit": limit})

            facts = []
            for record in records:
                facts.append({
                    "source": {
                        "id": record.get("source_node", ""),
                        "labels": record.get("source_labels", [])
                    },
                    "relationship1": record.get("relationship1", ""),
                    "intermediate": {
                        "id": record.get("intermediate_node", ""),
                        "labels": record.get("intermediate_labels", [])
                    },
                    "relationship2": record.get("relationship2", ""),
                    "target": {
                        "id": record.get("target_node", ""),
                        "labels": record.get("target_labels", [])
                    }
                })

            summaries = []
            for f in facts:
                part1 = f"{f['source']['id']} -[{f['relationship1']}]-> {f['intermediate']['id']}"
                if f["relationship2"] and f["target"]["id"]:
                    part2 = f" -[{f['relationship2']}]-> {f['target']['id']}"
                    summaries.append(part1 + part2)
                else:
                    summaries.append(part1)

            return "\n".join(summaries)

        except Exception as e:
            logging.error(f"[KG] Failed to retrieve structured KG facts: {e}")
            return []

    def add_fact_check_result(self, claim: str, result: Dict[str, Any], related_entities: List[str]) -> bool:
        """
        Store a fact-check result in the knowledge graph.

        Args:
            claim: The evaluated claim text.
            result: The structured result from the fact-checking agent.
            related_entities: List of entity IDs mentioned in the claim.

        Returns:
            True if added successfully, False otherwise.
        """
        try:
            # Create FactCheck node with timestamped ID
            factcheck_id = f"factcheck://{datetime.now().strftime('%Y%m%d%H%M%S')}/{abs(hash(claim))}"

            self.graph.query("""
            MERGE (f:FactCheck {id: $id})
            SET f.claim = $claim,
                f.verdict = $verdict,
                f.confidence_score = $confidence_score,
                f.reasoning = $reasoning,
                f.timestamp = $timestamp
            """, {
                "id": factcheck_id,
                "claim": claim,
                "verdict": result.get("verdict"),
                "confidence_score": result.get("confidence_score", 0),
                "reasoning": result.get("reasoning", ""),
                "timestamp": datetime.now().isoformat()
            })

            # Connect FactCheck to related entities
            for entity_id in related_entities:
                self.graph.query("""
                MATCH (e) WHERE e.id = $entity_id
                MATCH (f:FactCheck {id: $factcheck_id})
                MERGE (f)-[:MENTIONS]->(e)
                """, {
                    "entity_id": entity_id,
                    "factcheck_id": factcheck_id
                })

            return True
        except Exception as e:
            print(f"Error adding fact check to KG: {e}")
            return False