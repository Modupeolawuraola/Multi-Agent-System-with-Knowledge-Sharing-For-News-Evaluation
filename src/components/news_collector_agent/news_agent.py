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
        #get ;ast retrieved date from state or use default
        last_retrieved =state.get('last_retrieved_date')
        if last_retrieved:
            from_date= datetime.fromisoformat(last_retrieved)

        else:
            from_date = None

        #fectch article(you can modify the query based on your needs
        articles=news_tool.get_news_article(
            query="technology",
            from_date=from_date)

        #update state
        new_state['articles'] = articles
        new_state['last_retrieved_Date'] = datetime.now().isoformat()
        new_state['current_status']= 'collection_complete'

    except Exception as e:
        print(f"Error in new collection: {e}")
        new_state['current_status']= 'error: collection_failed'
        new_state['error'] = str(e)
    return new_state