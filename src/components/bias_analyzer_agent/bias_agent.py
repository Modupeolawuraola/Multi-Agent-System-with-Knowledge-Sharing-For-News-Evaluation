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


def bias_analyzer_agent(graph_state: GraphState) -> GraphState:
    """Main bias analysis node function"""
    # Only run diagnostic check if we're NOT in evaluation mode
    if os.environ.get("EVALUATION_MODE", "false").lower() != "true":
        diagnostic_check()

    logging.info("Starting bias analysis")

    if isinstance(graph_state, dict):
        graph_state = GraphState(**graph_state)

    new_state = graph_state.copy()

    # Unified article handling - combine both fields
    articles_to_analyze = []

    # Check for articles field (new format)
    if hasattr(graph_state, "articles") and isinstance(graph_state.articles, list):
        logging.info(f"Found {len(graph_state.articles)} articles in 'articles' field")
        articles_to_analyze = graph_state.articles.copy()

    # Check for article field (old format) - Add to articles if found
    if hasattr(graph_state, "article") and isinstance(graph_state.article, list):
        logging.info("Found article field - handling backward compatibility")
        # If we already have articles from the new format, don't override
        if not articles_to_analyze:
            articles_to_analyze = graph_state.article.copy()
            # Keep backward compatibility by maintaining the article field
            new_state.article = articles_to_analyze.copy()

    # Always use the articles field going forward
    new_state.articles = articles_to_analyze.copy()

    # No articles to analyze
    if not articles_to_analyze:
        logging.warning("No articles found to analyze")
        new_state.current_status = 'no_articles_to_analyze'
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
                # Passing article directly to the chain
                # Chain will call format_article internally
                result = analysis_chain.invoke(article)

                # Update article with analysis
                article_copy = article.copy()
                article_copy['bias_analysis'] = result
                analyzed_articles.append(article_copy)

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

        # Update the article field for backward compatibility if it was present
        if hasattr(new_state, "article"):
            new_state.article = analyzed_articles.copy()

        new_state.current_status = 'bias_analysis_complete'
        logging.info("Bias analysis completed successfully")

    except Exception as e:
        logging.error(f"Critical error in bias analysis: {str(e)}")
        # Preserve articles even on error
        if not hasattr(new_state, 'articles') or new_state.articles is None:
            new_state.articles = []

        # Update with error info but still provide complete required fields
        analyzed_articles = []
        for article in articles_to_analyze:
            article_copy = article.copy()
            article_copy['bias_analysis'] = {
                'error': str(e),
                'confidence_score': 0.0,
                'findings': [],
                'overall_assessment': 'Error during analysis',
                'recommendations': []
            }
            analyzed_articles.append(article_copy)

        new_state.articles = analyzed_articles

        # Update the article field for backward compatibility if it was present
        if hasattr(new_state, "article"):
            new_state.article = analyzed_articles.copy()

        new_state.current_status = 'bias_analysis_complete'  # Changed from 'error: analysis_failed' to maintain compatibility
        new_state.error = str(e)

    return new_state
