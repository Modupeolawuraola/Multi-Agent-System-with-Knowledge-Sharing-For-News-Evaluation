import logging
from src_v2.memory.schema import GraphState
from .tools import create_bias_analysis_chain, format_article
from src_v2.utils.aws_helpers import diagnostic_check
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

    # Check for bias query (direct analysis request) FIRST
    if hasattr(graph_state, "bias_query") and graph_state.bias_query:
        logging.info(f"Processing direct bias query: {graph_state.bias_query}")
        try:
            # Create analysis chain for the query
            analysis_chain = create_bias_analysis_chain()

            # Process the bias query directly
            query_result = analysis_chain.invoke({
                "content": graph_state.bias_query,
                "title": "Direct Query Analysis",
                "source": "User Query"
            })

            # Set the result in the state
            new_state.bias_analysis_result = {
                "query": graph_state.bias_query,
                "analysis": query_result
            }
            new_state.current_status = 'bias_query_analyzed'
            logging.info("Direct bias query analysis completed")
            return new_state
        except Exception as e:
            logging.error(f"Error analyzing bias query: {str(e)}")
            new_state.error = str(e)
            new_state.current_status = 'bias_query_analysis_failed'
            return new_state

    # THEN check for empty articles list
    if hasattr(graph_state, "articles") and graph_state.articles is not None:
        if len(graph_state.articles) == 0:
            logging.warning("Empty articles list provided")
            new_state.current_status = 'no_articles_to_analyze'
            return new_state

    # First check if articles are already in the state
    articles_to_analyze = []
    if hasattr(graph_state, "articles") and graph_state.articles and len(graph_state.articles) > 0:
        logging.info(f"Using {len(graph_state.articles)} articles from current state")
        articles_to_analyze = graph_state.articles
    # Otherwise get articles from the knowledge graph based on query
    elif hasattr(graph_state, "news_query") and graph_state.news_query:
        # Retrieve articles from KG based on query
        # Check if retrieve_related_articles exists on the knowledge_graph (it might be a mock)
        if hasattr(knowledge_graph, "retrieve_related_articles"):
            articles_to_analyze = knowledge_graph.retrieve_related_articles(
                query=graph_state.news_query,
                limit=5
            )
            logging.info(f"Retrieved {len(articles_to_analyze)} articles from knowledge graph based on query")
        else:
            logging.warning("Knowledge graph does not have retrieve_related_articles method")
            new_state.current_status = 'kg_retrieval_not_supported'
            return new_state
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
                # Always call add_bias_analysis if it exists
                if hasattr(knowledge_graph, "add_bias_analysis"):
                    knowledge_graph.add_bias_analysis(article_copy)
                    logging.info(f"Successfully added bias analysis to knowledge graph: {article.get('title', 'Untitled')}")
                else:
                    logging.warning("Knowledge graph does not have add_bias_analysis method")

                logging.info(f"Successfully analyzed article: {article.get('title', 'Untitled')}")
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
        logging.info("Bias analysis completed successfully")

    except Exception as e:
        logging.error(f"Critical error in bias analysis: {str(e)}")
        # Preserve articles even on error
        if not hasattr(new_state, 'articles') or new_state.articles is None:
            new_state.articles = []

        new_state.current_status = 'bias_analysis_failed'
        new_state.error = str(e)

    return new_state