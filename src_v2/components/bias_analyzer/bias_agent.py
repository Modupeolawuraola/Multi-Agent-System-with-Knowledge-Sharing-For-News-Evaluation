# src_v2/components/bias_analyzer/bias_agent.py
import logging
from src.memory.schema import GraphState
from .tools import create_bias_analysis_chain, format_article
from src.utils.aws_helpers import diagnostic_check
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bias_analyzer.log"),
        logging.StreamHandler()
    ]
)


def bias_analyzer_agent(graph_state: GraphState, knowledge_graph) -> GraphState:
    """
    Bias analysis agent that directly interacts with the knowledge graph
    
    Args:
        graph_state: Current state of the system
        knowledge_graph: KnowledgeGraph instance for direct interaction
    
    Returns:
        Updated graph state
    """
    # Only run diagnostic check if we're NOT in evaluation mode
    if os.environ.get("EVALUATION_MODE", "false").lower() != "true":
        diagnostic_check()

    logging.info("Starting direct KG bias analysis")

    if isinstance(graph_state, dict):
        graph_state = GraphState(**graph_state)

    new_state = graph_state.copy()

    # Get article from the knowledge graph based on query
    if hasattr(graph_state, "news_query") and graph_state.news_query:
        # Retrieve articles from KG based on query
        articles_to_analyze = knowledge_graph.retrieve_related_articles(
            query=graph_state.news_query, 
            limit=5
        )
        logging.info(f"Retrieved {len(articles_to_analyze)} articles from knowledge graph based on query")
    else:
        logging.warning("No query provided for retrieving articles from knowledge graph")
        new_state.current_status = 'no_query_for_kg'
        return new_state

    # No articles found in knowledge graph
    if not articles_to_analyze:
        logging.warning("No articles found in knowledge graph matching query")
        new_state.current_status = 'no_articles_found_in_kg'
        return new_state

    # making sure articles exist even if there is an error
    try:
        # Create analysis chain
        analysis_chain = create_bias_analysis_chain()

        # Analyze each article
        analyzed_articles = []
        for i, article in enumerate(articles_to_analyze):
            try:
                logging.info(
                    f"Analyzing article {i + 1}/{len(articles_to_analyze)}: {article.get('title', 'Untitled')}")

                # Format and analyze
                result = analysis_chain.invoke(article)

                # Update article with analysis
                article_copy = article.copy()
                article_copy['bias_analysis'] = result
                analyzed_articles.append(article_copy)

                # Add bias analysis directly to knowledge graph
                knowledge_graph.add_bias_analysis(article_copy)

                logging.info(f"Successfully analyzed article and updated knowledge graph: {article.get('title', 'Untitled')}")
            except Exception as e:
                logging.error(f"Error analyzing article {article.get('title', 'Untitled')}: {str(e)}")
                article_copy = article.copy()
                article_copy['bias_analysis'] = {
                    'error': str(e),
                    'confidence_score': 0.0,
                    'findings': [],
                    'overall_assessment': 'Error during analysis',
                    'recommendations': []
                }
                analyzed_articles.append(article_copy)

        # Update state with analyzed articles
        new_state.articles = analyzed_articles
        new_state.current_status = 'bias_analysis_complete'
        logging.info("Bias analysis completed successfully and KG updated")

    except Exception as e:
        logging.error(f"Critical error in bias analysis: {str(e)}")
        # Preserve articles even on error
        if not hasattr(new_state, 'articles') or new_state.articles is None:
            new_state.articles = []

        new_state.current_status = 'bias_analysis_failed'
        new_state.error = str(e)

    return new_state
