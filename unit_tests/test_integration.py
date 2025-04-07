import logging
import os
from typing import List, Dict, Any
from src.memory.schema import GraphState
from src.components.bias_analyzer_agent.bias_agent import bias_analyzer_agent
from src.components.fact_checker_agent.fact_checker_Agent import fact_checker_agent
from langchain_neo4j import Neo4jGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system.log"),
        logging.StreamHandler()
    ]
)


def get_neo4j_connection():
    """Create a connection to the Neo4j database"""
    try:
        graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        return graph
    except Exception as e:
        logging.error(f"Error connecting to Neo4j: {e}")
        raise


def process_articles(articles: List[Dict[str, Any]], use_kg: bool = True) -> List[Dict[str, Any]]:
    """Process articles through each component sequentially with error handling"""
    results = []

    # Connect to Neo4j if using KG
    kg = None
    if use_kg:
        try:
            kg = get_neo4j_connection()
        except Exception as e:
            logging.error(f"Failed to connect to knowledge graph: {e}")
            # Continue without KG if connection fails

    for article in articles:
        try:
            # Step 1: Run bias analysis
            bias_state = bias_analyzer_agent(GraphState(articles=[article]))

            if hasattr(bias_state, "articles") and bias_state.articles:
                processed_article = bias_state.articles[0]

                # Step 2: Attempt fact checking with proper error handling
                try:
                    fact_state = fact_checker_agent(GraphState(articles=[processed_article]))
                    if hasattr(fact_state, "articles") and fact_state.articles:
                        processed_article = fact_state.articles[0]
                    else:
                        # Fallback for fact-checking
                        processed_article['fact_check'] = {
                            'verified_claims': [],
                            'report': {'overall_verdict': 'processing_failed'}
                        }
                        logging.warning(f"Fact-checking failed for article: {article.get('title', 'Unknown')}")
                except Exception as e:
                    # Log and continue with just bias analysis
                    logging.error(f"Error in fact-checking: {str(e)}")
                    processed_article['fact_check'] = {
                        'verified_claims': [],
                        'report': {'overall_verdict': 'error', 'message': str(e)}
                    }

                # Step 3: Update knowledge graph if available
                if kg and use_kg:
                    try:
                        # Add the article to the knowledge graph
                        add_article_to_kg(kg, processed_article)
                        processed_article['kg_status'] = 'added_to_kg'
                    except Exception as e:
                        logging.error(f"Error adding article to KG: {e}")
                        processed_article['kg_status'] = f'kg_error: {str(e)}'

                # Add to results
                results.append(processed_article)
            else:
                logging.warning(f"Bias analysis produced no output for: {article.get('title', 'Unknown')}")
                # Add the original article with a note
                article['bias_analysis'] = {'status': 'failed', 'message': 'No output from bias analyzer'}
                article['fact_check'] = {'status': 'skipped', 'message': 'Bias analysis failed'}
                results.append(article)
        except Exception as e:
            logging.error(f"Error processing article: {article.get('title', 'Unknown')} - {str(e)}")
            # Add minimal result with error info
            article['processing_error'] = str(e)
            article['bias_analysis'] = {'status': 'error', 'message': str(e)}
            article['fact_check'] = {'status': 'skipped', 'message': 'Error in processing pipeline'}
            results.append(article)

    return results


def add_article_to_kg(kg, article):
    """Add an article to the knowledge graph"""
    # Create the article node
    kg.query(
        """
        MERGE (a:Article {url: $url})
        SET a.source_name = $source_name,
            a.author = $author,
            a.title = $title,
            a.content = $content,
            a.date = $date
        """,
        {
            "url": article.get("url", ""),
            "source_name": article.get("source", ""),
            "author": article.get("author", ""),
            "title": article.get("title", ""),
            "content": article.get("content", ""),
            "date": article.get("date", "")
        }
    )

    # Add bias analysis if available
    if "bias_analysis" in article:
        kg.query(
            """
            MATCH (a:Article {url: $url})
            MERGE (b:BiasAnalysis {article_url: $url})
            SET b.confidence_score = $confidence_score,
                b.overall_assessment = $overall_assessment,
                b.findings = $findings
            MERGE (a)-[:HAS_BIAS_ANALYSIS]->(b)
            """,
            {
                "url": article.get("url", ""),
                "confidence_score": article.get("bias_analysis", {}).get("confidence_score", 0),
                "overall_assessment": article.get("bias_analysis", {}).get("overall_assessment", ""),
                "findings": str(article.get("bias_analysis", {}).get("findings", []))
            }
        )

    # Add fact check if available
    if "fact_check" in article:
        kg.query(
            """
            MATCH (a:Article {url: $url})
            MERGE (f:FactCheck {article_url: $url})
            SET f.overall_verdict = $overall_verdict,
                f.verified_claims = $verified_claims
            MERGE (a)-[:HAS_FACT_CHECK]->(f)
            """,
            {
                "url": article.get("url", ""),
                "overall_verdict": article.get("fact_check", {}).get("report", {}).get("overall_verdict", ""),
                "verified_claims": str(article.get("fact_check", {}).get("verified_claims", []))
            }
        )


def process_single_article(article: Dict[str, Any], use_kg: bool = True) -> Dict[str, Any]:
    """Process a single article through the simplified workflow"""
    results = process_articles([article], use_kg)
    return results[0] if results else article


def process_with_knowledge_graph(article: Dict[str, Any], kg_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Process an article using existing knowledge graph data for reference."""
    # This function should process the article using knowledge graph data
    # that's already been passed in, rather than connecting to a Neo4j instance

    # First do regular processing
    processed_article = process_single_article(article, use_kg=False)

    # Then enrich with knowledge graph information if relevant
    # This is a simplified version - customize based on actual requirements
    if "articles" in kg_data:
        for kg_article in kg_data["articles"]:
            # Look for similar content/topics
            if (article.get("content", "") and kg_article.get("content", "") and
                    any(term in article["content"] for term in kg_article["content"].split())):
                # Enhance the fact check with existing knowledge
                if "fact_check" in kg_article and "fact_check" in processed_article:
                    processed_article["fact_check"]["kg_reference"] = {
                        "url": kg_article.get("url", ""),
                        "title": kg_article.get("title", ""),
                        "prior_verification": kg_article["fact_check"].get("verified_claims", [])
                    }
                break

    return processed_article

def retrieve_related_articles(query: str, limit: int = 5):
    """Retrieve articles from the knowledge graph related to a query"""
    try:
        kg = get_neo4j_connection()

        # Simple query to find related articles
        results = kg.query(
            """
            MATCH (a:Article)
            WHERE a.title CONTAINS $query OR a.content CONTAINS $query
            RETURN a.title, a.source_name, a.url, a.date
            LIMIT $limit
            """,
            {
                "query": query,
                "limit": limit
            }
        )

        return results
    except Exception as e:
        logging.error(f"Error retrieving from KG: {e}")
        return []
