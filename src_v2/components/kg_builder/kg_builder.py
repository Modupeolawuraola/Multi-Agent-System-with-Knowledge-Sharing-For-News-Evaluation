import os, json
import boto3
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from langchain_aws import ChatBedrock
from langchain_community.graphs.graph_document import Node, Relationship
import requests
from newspaper import Article
from datetime import datetime, timedelta, date
import glob
import logging

# Load environment variables
load_dotenv()


class KnowledgeGraph:
    """
    Knowledge Graph component that handles direct interaction with Neo4j,
    fetching news articles, and building the knowledge graph.
    """

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
                "Article", "News Source", "Bias", "Fact Check",
                "Person", "Organization", "Event", "Policy", "Issue",
                "Location", "Election", "Bill", "Vote", "Speech", "Alliance"
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

        # Create vector index
        self.create_vector_index()

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

    def fetch_news_articles(self, query="politics", days=1, limit=10, store_in_kg=True):
        """
        Fetch articles directly from NewsAPI.
        Replaces the news collector agent functionality

        Args:
            query (str): Search query
            days (int): How many days back to search
            limit (int): Maximum number of articles to return
            store_in_kg (bool): Whether to store articles in the knowledge graph

        Returns:
            list: Processed articles
        """
        NEWS_API_KEY = os.getenv('NEWS_API_KEY')
        if not NEWS_API_KEY:
            raise ValueError("NEWS_API_KEY environment variable is not set")

        # Check if we're in evaluation mode
        evaluation_mode = os.environ.get("EVALUATION_MODE", "false").lower() == "true"

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        from_date = start_date.strftime('%Y-%m-%d')

        # Prepare API request to NewsAPI
        base_url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'publishedAt',
            'apiKey': NEWS_API_KEY,
            'language': 'en',
            'pageSize': limit
        }

        try:
            # Send request
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            articles = response.json()['articles']

            # Format articles to match schema and get full content
            formatted_articles = []
            for article in articles:
                try:
                    # Try to get full article text using newspaper3k
                    url = article.get('url')
                    news_article = Article(url)
                    news_article.download()
                    news_article.parse()

                    formatted_article = {
                        'title': article.get('title'),
                        'content': article.get('content'),
                        'full_content': news_article.text,
                        'source': article.get('source', {}).get('name'),
                        'date': article.get('publishedAt'),
                        'url': url,
                        'author': article.get('author')
                    }

                    formatted_articles.append(formatted_article)
                    print(f"Processed article: {article.get('title')}")

                    # Add article to knowledge graph ONLY if not in evaluation mode and store_in_kg is True
                    if store_in_kg and not evaluation_mode:
                        self.add_article(formatted_article)
                        print(f"Added article to KG: {article.get('title')}")
                    else:
                        print(f"Skipped adding to KG (evaluation mode or store_in_kg=False): {article.get('title')}")

                except Exception as e:
                    print(f"Error processing article {article.get('title', 'Unknown')}: {e}")

            return formatted_articles
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def add_article(self, article):
        """Add a single article to the knowledge graph"""
        # Check if we're in evaluation mode - return early if so
        evaluation_mode = os.environ.get("EVALUATION_MODE", "false").lower() == "true"
        if evaluation_mode:
            print(f"Skipping add_article in evaluation mode: {article.get('title', 'Untitled')}")
            return True

        source = article.get("source")
        source_name = source["name"] if isinstance(source, dict) else source

        author = article.get("author")
        published_at = article.get("date") or article.get("publishedAt")
        url = article.get("url")
        title = article.get("title")
        full_content = article.get("full_content") or article.get("content", "")
        bias = article.get("bias", {})

        # Create a LangChain Document with metadata
        article_doc = [
            Document(
                page_content=full_content,
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
                        type="mentions"
                    )
                )

        # Add the generated nodes and relationships to the graph
        self.graph.add_graph_documents(graph_docs)

        # Add bias analysis if available
        if "bias_analysis" in article or "bias" in article:
            self.add_bias_analysis(article)

        # Add fact check if available
        if "fact_check" in article:
            self.add_fact_check(article)

        return True

    def add_bias_analysis(self, article):
        """Add bias analysis data to the knowledge graph"""
        # Check if we're in evaluation mode - return early if so
        evaluation_mode = os.environ.get("EVALUATION_MODE", "false").lower() == "true"
        if evaluation_mode:
            print(f"Skipping add_bias_analysis in evaluation mode: {article.get('title', 'Untitled')}")
            return True

        url = article.get("url")
        bias_analysis = article.get("bias_analysis", article.get("bias", {}))

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
        # Check if we're in evaluation mode - return early if so
        evaluation_mode = os.environ.get("EVALUATION_MODE", "false").lower() == "true"
        if evaluation_mode:
            print(f"Skipping add_fact_check in evaluation mode: {article.get('title', 'Untitled')}")
            return True

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

    def add_articles_from_json(self, filename):
        """Add articles from a JSON file to the knowledge graph"""
        # Check if we're in evaluation mode - return early if so
        evaluation_mode = os.environ.get("EVALUATION_MODE", "false").lower() == "true"
        if evaluation_mode:
            print(f"Skipping add_articles_from_json in evaluation mode: {filename}")
            with open(filename, encoding="utf-8") as json_file:
                articles_data = json.load(json_file)
            articles = articles_data.get('articles', [])
            return len(articles)

        with open(filename, encoding="utf-8") as json_file:
            articles_data = json.load(json_file)
        articles = articles_data.get('articles', [])

        for article in articles:
            self.add_article(article)

        return len(articles)

    def merge_json_files(self, input_dir, output_path):
        """Merge multiple JSON files into one"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        json_files = glob.glob(os.path.join(input_dir, "*.json"))

        merged_data = {"status": "ok", "totalResults": 0, "articles": []}

        for file in json_files:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "articles" in data:
                    merged_data["articles"].extend(data["articles"])
                    merged_data["totalResults"] += data.get("totalResults", len(data["articles"]))

        # Deduplicate by URL
        unique_articles = {a["url"]: a for a in merged_data["articles"]}
        merged_data["articles"] = list(unique_articles.values())
        merged_data["totalResults"] = len(merged_data["articles"])

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, indent=2)

        return merged_data

    def get_dates_between(self, start_date_str, end_date_str):
        """Generate a list of dates between two dates (inclusive)"""
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        return dates

    def fetch_news_for_daterange(self, start_date, end_date, query="politics", output_dir="news_jsons"):
        """Fetch news for a date range and build KG"""
        # Check if we're in evaluation mode
        evaluation_mode = os.environ.get("EVALUATION_MODE", "false").lower() == "true"

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Get list of dates
        date_list = self.get_dates_between(start_date, end_date)

        all_articles = []

        # For each date, fetch articles
        for date_str in date_list:
            print(f"Fetching news for {date_str}...")
            articles = self.fetch_news_articles(query=query, days=1, store_in_kg=not evaluation_mode)
            all_articles.extend(articles)

            # Save to JSON for this date
            output_file = f"{output_dir}/political_news_{date_str}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({"articles": articles}, f, indent=4)

        # Merge all the JSON files
        merged_file = f"{output_dir}/all_articles_{start_date}-{end_date}.json"
        self.merge_json_files(output_dir, merged_file)

        print(f"Processed {len(all_articles)} articles across {len(date_list)} days")
        if evaluation_mode:
            print("⚠️ Running in EVALUATION MODE - articles were NOT stored in the KG")
        return all_articles
