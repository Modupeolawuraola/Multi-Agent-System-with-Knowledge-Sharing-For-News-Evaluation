import os
import sys
import logging
import json
from typing import Dict, List, TypedDict, Optional
import boto3
from langchain_neo4j import Neo4jGraph

# Add the root directory to the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)

from src.memory.schema import GraphState
from src_v2.components.summarizer.tools import create_summarization_chain, format_article
from src_v2.utils.aws_helpers import get_aws_credentials, diagnostic_check

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Run AWS diagnostic check
diagnostic_check()

class GraphState(TypedDict):
    """shared state schema that all agents can access"""
    articles: List[Dict]
    current_status: str
    error: Optional[str]

def summarizer_agent(state: GraphState) -> GraphState:
    """Summarizer agent that processes articles and updates the knowledge graph"""
    try:
        # Get articles from state
        articles = state.get("articles", [])
        if not articles:
            logger.warning("No articles found in state")
            return state

        # Create summarization chain
        chain = create_summarization_chain()

        # Process each article
        for article in articles:
            try:
                # Format article for analysis
                formatted_article = format_article(article)
                
                # Get summary and relationship analysis
                result = chain.invoke(formatted_article)
                
                # Update article with results
                if isinstance(result, dict):
                    article["summary"] = result.get("content_summary", "")
                    article["relationship_analysis"] = result.get("relationship_analysis", "")
                else:
                    article["summary"] = str(result)
                    article["relationship_analysis"] = ""
                
                logger.info(f"Successfully processed article: {article['url']}")
                
            except Exception as e:
                logger.error(f"Error processing article {article.get('url', 'unknown')}: {str(e)}")
                article["error"] = str(e)

        # Update state with processed articles
        state["articles"] = articles
        state["current_status"] = "summarized"
        
        return state
        
    except Exception as e:
        logger.error(f"Error in summarizer agent: {str(e)}")
        state["error"] = str(e)
        return state 