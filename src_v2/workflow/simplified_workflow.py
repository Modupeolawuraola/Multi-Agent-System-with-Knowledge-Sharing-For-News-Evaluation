import logging
import os
from typing import List, Dict, Any
from src_v2.memory.schema import GraphState
# from src_v2.components.bias_analyzer.bias_agent import bias_analyzer_agent
from src_v2.components.bias_analyzer.bias_agent_update import bias_analyzer_agent
# from src_v2.components.fact_checker.fact_checker_Agent import fact_checker_agent
from src_v2.components.fact_checker.fact_checker_updated import fact_checker_agent
from src_v2.components.kg_builder.kg_builder import KnowledgeGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system.log"),
        logging.StreamHandler()
    ]
)

def normalize_article_fields(article: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all necessary fields exist before agent processing."""
    article['full_content'] = article.get('full_content') or article.get('content') or ''
    article['source'] = article.get('source') or article.get('source_name') or 'Unknown Source'
    article['date'] = article.get('date') or article.get('publishedAt') or 'Unknown Date'
    return article

def process_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process articles through the simplified workflow with direct KG interaction"""
    results = []

    # Initialize Knowledge Graph once for all articles
    try:
        kg = KnowledgeGraph()
        logging.info("Successfully initialized Knowledge Graph")
    except Exception as e:
        logging.error(f"Failed to initialize Knowledge Graph: {e}")
        # Create placeholder for KG to avoid None references
        kg = None

    # First, add all articles to the KG
    if kg:
        for article in articles:
            try:
                kg.add_article(article)
                logging.info(f"Added article to KG: {article.get('title', 'Unknown')}")
            except Exception as e:
                logging.error(f"Error adding article to KG: {e}")

    # Process each article individually
    for article in articles:
        try:
            article = normalize_article_fields(article)

            # Step 1: Create initial state
            initial_state = GraphState(articles=[article])

            # Step 2: Run bias analysis with direct KG access
            bias_state = bias_analyzer_agent(initial_state, kg)

            if hasattr(bias_state, "articles") and bias_state.articles:
                processed_article = bias_state.articles[0]

                # Step 3: Run fact checking with direct KG access
                try:
                    fact_state = fact_checker_agent(GraphState(articles=[processed_article]), kg)
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


def process_direct_query(query: str, query_type="fact_check"):
    """
    Process a direct user query with KG lookup.

    Args:
        query: User query text
        query_type: Type of query ("fact_check" or "bias")

    Returns:
        Results of the query processing
    """
    try:
        # Initialize Knowledge Graph
        kg = KnowledgeGraph()

        # Create initial state based on query type
        if query_type == "fact_check":
            state = GraphState(news_query=query)
            # Process with fact checker
            result_state = fact_checker_agent(state, kg)
            return result_state
        elif query_type == "bias":
            state = GraphState(bias_query=query)
            # Process with bias analyzer
            result_state = bias_analyzer_agent(state, kg)
            return result_state
        else:
            logging.error(f"Unknown query type: {query_type}")
            return GraphState(error=f"Unknown query type: {query_type}")
    except Exception as e:
        logging.error(f"Error processing direct query: {e}")
        return GraphState(error=str(e))


def retrieve_related_articles(query: str, limit: int = 5):
    """Retrieve articles from the knowledge graph related to a query"""
    try:
        kg = KnowledgeGraph()
        return kg.retrieve_related_articles(query, limit)
    except Exception as e:
        logging.error(f"Error retrieving from KG: {e}")
        return []