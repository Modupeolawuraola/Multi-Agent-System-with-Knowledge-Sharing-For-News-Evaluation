from ...memory.schema import GraphState, NewsArticle
from .tools import NewsAPI
from datetime import datetime
from typing import List


def new_collector_Agent(state: GraphState) -> GraphState:
    """Collect news articles from external source API"""
    new_state= state.copy()

    #initialize NewsAPI tools
    news_tool = NewsAPI()

    try:
        #get last retrieved date from state or use default
        last_retrieved =state.get('last_retrieved_date')
        if last_retrieved:
            from_date= datetime.fromisoformat(last_retrieved)

        else:
            from_date = None

        #fectch article
        articles=news_tool.get_news_article(
            query="technology",
            from_date=from_date)

        #ensure we have a valid list articles
        if not isinstance(articles, list):
            articles=[]

        #update state
        new_state['articles'] = articles
        new_state['last_retrieved_Date'] = datetime.now().isoformat()
        new_state['current_status']= 'collection_complete'

    except Exception as e:
        print(f"Error in new collection: {e}")

        #ensure articles key exists on error
        if 'articles' not in new_state:
            new_state['articles'] = []
        new_state['current_status']= 'error: collection_failed'
        new_state['error'] = str(e)
    return new_state