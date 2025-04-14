import logging
import os
from typing import List, Dict, Any, Optional
from src_v3.memory.schema import GraphState
# from src_v3.components.bias_analyzer.bias_agent import bias_analyzer_agent
from src_v3.components.bias_analyzer.bias_agent_update import bias_analyzer_agent
# from src_v3.components.fact_checker.fact_checker_Agent import fact_checker_agent
from src_v3.components.fact_checker.fact_checker_updated import fact_checker_agent
from src_v3.components.kg_builder.kg_builder import KnowledgeGraph

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
    article['title'] = article.get('title') or 'Unknown Title'
    article['source'] = article.get('source') or article.get('source_name') or 'Unknown Source'
    article['date'] = article.get('date') or article.get('publishedAt') or 'Unknown Date'
    return article

def process_articles(graph_state: GraphState, knowledge_graph: Optional[object] = None) -> GraphState:
    """Evaluate bias of articles using knowledge graph context, without modifying the KG."""
    results = []

    # Initialize Knowledge Graph for querying
    kg = knowledge_graph
    if kg is None:
        try:
            from src_v3.memory.knowledge_graph import KnowledgeGraph
            kg = KnowledgeGraph()
            logging.info("Knowledge Graph initialized for bias analysis (query-only mode)")
        except Exception as e:
            logging.error(f"Knowledge Graph initialization failed: {e}")
            kg = None

    # Evaluate each article
    for article in graph_state.articles:
        try:
            article = normalize_article_fields(article)

            # Step 1: Create single-article state
            single_state = GraphState(articles=[article])

            # Step 2: Run bias analyzer agent (uses KG context only)
            bias_state = bias_analyzer_agent(single_state, kg)

            if hasattr(bias_state, "articles") and bias_state.articles:
                processed_article = bias_state.articles[0]
                results.append(processed_article)
            else:
                logging.warning(f"Bias analysis failed for article: {article.get('title', 'Unknown')}")
                article['bias_analysis'] = {'status': 'failed', 'message': 'No output from bias analyzer'}
                results.append(article)

        except Exception as e:
            logging.error(f"Error processing article: {article.get('title', 'Unknown')} - {str(e)}")
            article['processing_error'] = str(e)
            article['bias_analysis'] = {'status': 'error', 'message': str(e)}
            results.append(article)

    # Update and return new graph state
    graph_state.articles = results
    graph_state.current_status = "bias_evaluated"
    return graph_state

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