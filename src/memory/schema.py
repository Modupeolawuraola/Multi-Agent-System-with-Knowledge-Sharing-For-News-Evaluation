from typing import List, Dict, TypedDict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class NewsArticle(TypedDict):
    title: str
    content: str
    source: str
    date: str
    url: str
    bias_analysis: Optional[Dict]
    fact_check: Optional[Dict]  # For articles processed through the system

# For articles processed through the system
class GraphState(BaseModel):
    """Shared state schema that all agents can access"""
    knowledge_graph: Dict = Field(default_factory=dict)
    articles: List[Dict] = Field(default_factory=list)  # Standardized on 'articles' (plural)
    article: List[Dict] = Field(default_factory=list)  # Added for backward compatibility
    last_retrieved_date: Optional[str] = None
    current_status: str = "ready"
    bias_agent: Optional[Dict] = None
    error: Optional[str] = None
    news_query: Optional[str] = None  # For direct fact-checking queries from users
    fact_check_result: Optional[Dict] = None  # For storing direct query fact-check results
    matched_articles: Optional[List[Dict]] = None  # For storing articles from KG that match a query
    retrieved_articles: Optional[List[Dict]] = None  # For storing articles retrieved from KG
    updated_data: Optional[List[Dict]] = None  # For storing data that was updated in KG

    def copy(self):
        """Create a proper copy that returns a GraphState, not a dict"""
        return GraphState(**self.dict())

