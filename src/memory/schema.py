from typing import List, Dict, TypedDict, Optional
from datetime import datetime


class NewsArticle(TypedDict):
    title:str
    content:str
    source:str
    date: str
    url:str
    bias_analysis:Optional[Dict]



class GraphState(TypedDict):
    """shared state schema that all agents can access"""
    knowledge_graph:Dict
    article:List[NewsArticle]
    last_retrieved_date:Optional[str]
    current_status:str
    bias_agent:Optional[Dict]
    current_status:str
    error:Optional[str]
