
from ...memory.schema import GraphState
from .tools import create_bias_analysis_chain, format_article


def bias_analyzer_agent(graph_state: GraphState) -> GraphState:
    """Main bias analysis node function"""
    new_state = graph_state.copy()

    try:
        # Create analysis chain
        analysis_chain = create_bias_analysis_chain()

        # Analyze each article
        analyzed_articles = []
        if 'articles' not in graph_state:
            raise KeyError("No articles found in state")

        for article in graph_state['articles']:
            try:
                # format and analyze
                article_text = format_article(article)
                result = analysis_chain.invoke("article_text", article_text)

                # Update article with analysis
                article_copy = article.copy()
                article_copy['bias_analysis'] = result
                analyzed_articles.append(article_copy)

            except Exception as e:
                print(f"Error analyzing article: {e}")
                article_copy = article.copy()
                article_copy['bias_analysis'] = {'error': str(e)}
                analyzed_articles.append(article_copy)

        # Update state
        new_state['articles'] = analyzed_articles
        new_state['current_status'] = 'bias_analysis_complete'

    except Exception as e:
        print(f"Error in bias analysis: {e}")
        new_state['current_status'] = 'error: analysis_failed'
        new_state['error'] = str(e)

    return new_state