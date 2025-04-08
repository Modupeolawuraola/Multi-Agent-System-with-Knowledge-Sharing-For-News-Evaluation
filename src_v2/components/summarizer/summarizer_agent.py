import os
import sys

# Add the root directory to the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_dir)

import logging
import json
from src.memory.schema import GraphState
from src_v2.components.summarizer.tools import create_summarization_chain, format_article
from src_v2.utils.aws_helpers import get_aws_credentials, diagnostic_check
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("summarizer.log"),
        logging.StreamHandler()
    ]
)

def summarizer_agent(graph_state: GraphState, knowledge_graph) -> GraphState:
    """
    Summarizer agent that analyzes articles and their relationships in the knowledge graph
    
    Args:
        graph_state: Current state of the system
        knowledge_graph: KnowledgeGraph instance for direct interaction
    
    Returns:
        Updated graph state
    """
    # Only run diagnostic check if we're NOT in evaluation mode
    if os.environ.get("EVALUATION_MODE", "false").lower() != "true":
        diagnostic_check()

    logging.info("Starting summarizer agent")

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
        logging.info(f"Retrieved {len(articles_to_analyze)} articles from knowledge graph")
    else:
        logging.warning("No query provided for retrieving articles")
        new_state.current_status = 'no_query_for_kg'
        return new_state

    if not articles_to_analyze:
        logging.warning("No articles found in knowledge graph")
        new_state.current_status = 'no_articles_found_in_kg'
        return new_state

    try:
        # Create summarization chain
        summarization_chain = create_summarization_chain()

        # Analyze each article
        analyzed_articles = []
        for i, article in enumerate(articles_to_analyze):
            try:
                logging.info(f"Analyzing article {i + 1}/{len(articles_to_analyze)}: {article.get('title', 'Untitled')}")

                # Format and analyze
                formatted_article = format_article(article)
                result = summarization_chain.invoke(formatted_article)

                # Update article with summaries
                article_copy = article.copy()
                article_copy['content_summary'] = result['content_summary']
                article_copy['relationship_analysis'] = result['relationship_analysis']
                analyzed_articles.append(article_copy)

                # Add summaries to knowledge graph
                knowledge_graph.add_summaries(article_copy)

                logging.info(f"Successfully analyzed article and updated knowledge graph: {article.get('title', 'Untitled')}")
            except Exception as e:
                logging.error(f"Error analyzing article {article.get('title', 'Untitled')}: {str(e)}")
                article_copy = article.copy()
                article_copy['content_summary'] = f"Error during analysis: {str(e)}"
                article_copy['relationship_analysis'] = f"Error during analysis: {str(e)}"
                analyzed_articles.append(article_copy)

        # Update state with analyzed articles
        new_state.articles = analyzed_articles
        new_state.current_status = 'summarization_complete'
        logging.info("Summarization completed successfully")

    except Exception as e:
        logging.error(f"Critical error in summarization: {str(e)}")
        if not hasattr(new_state, 'articles') or new_state.articles is None:
            new_state.articles = []
        new_state.current_status = 'summarization_failed'
        new_state.error = str(e)

    return new_state 