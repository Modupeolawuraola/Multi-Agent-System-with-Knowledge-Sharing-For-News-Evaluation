from typing import List, Dict, TypedDict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import json
import logging

class NewsArticle(TypedDict):
    title: str
    content: str
    source: str
    date: str
    url: str
    bias_analysis: Optional[Dict]
    fact_check: Optional[Dict]

# For articles processed through the system
class GraphState(BaseModel):
    """Shared state schema that all agents can access - simplified for direct KG interaction"""
    articles: List[Dict] = Field(default_factory=list)  # Standardized on 'articles' (plural)
    current_status: str = "ready"
    error: Optional[str] = None
    news_query: Optional[str] = None  # For direct fact-checking queries
    bias_query: Optional[str] = None  # For direct bias analysis queries
    fact_check_result: Optional[Dict] = None  # For storing direct query fact-check results
    bias_analysis_result: Optional[Dict] = None  # For storing direct bias analysis results
    matched_articles: Optional[List[Dict]] = None  # For storing articles from KG that match a query

    @validator('articles', pre=True)
    def parse_json_strings(cls, articles):
        """Parse any string articles as JSON"""
        parsed_articles = []
        for article in articles:
            if isinstance(article, str):
                try:
                    parsed_articles.append(json.loads(article))
                except json.JSONDecodeError as e:
                    logging.error(f"Skipping string article, failed to parse JSON: {e}")
                    continue
            else:
                parsed_articles.append(article)
        return parsed_articles

    def copy(self):
        """Create a proper copy that returns a GraphState, not a dict"""
        return GraphState(**self.model_dump())  # Updated to use model_dump() instead of dict()