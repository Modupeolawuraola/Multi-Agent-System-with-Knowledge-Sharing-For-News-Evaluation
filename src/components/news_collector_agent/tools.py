import requests
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
import boto3


load_dotenv()
from .news_prompt import (
query_generation_prompt,
article_filter_prompt,
source_validation_prompt
)

class NewsAPI:
    def __init__(self):
        self.api_key = os.environ.get('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("NEWS_API_KEY environment variable is not set")

        self.base_url = "https://newsapi.org/v2/everything"

        # Initialize AWS Bedrock - no fallback to mock
        client = boto3.client("bedrock-runtime", region_name="us-east-1")
        self.llm = ChatBedrock(
            client=client,
            model_id='anthropic.claude-3-sonnet-20240229-v1:0',
            model_kwargs={"temperature":0.2}
        )

    def get_news_article(self, query:str, from_date: datetime=None) -> List[Dict]:
        """Fetch articles from NEWSAPI"""
        if from_date is None:
            from_date=datetime.now()- timedelta(days=1)

        # Use LLM to enhance query if available
        try:
            # You could implement query enhancement using the LLM here
            enhanced_query = query  # For now, just use the original query
        except Exception as e:
            print(f"Error enhancing query with LLM: {e}")
            enhanced_query = query

        params={
            'q': enhanced_query,
            'from': from_date.strftime('%Y-%m-%d'),
            'sortBy': 'publishedAt',
            'apiKey': self.api_key,
            'language': 'en'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            articles = response.json()['articles']

            # Format article to match schema
            formatted_articles = []
            for article in articles:
                formatted_article= {
                    'title': article.get('title'),
                    'content': article.get('content'),
                    'source': article.get('source', {}).get('name'),
                    'date': article.get('publishedAt'),
                    'url': article.get('url'),
                    'bias_analysis': None
                }

                formatted_articles.append(formatted_article)

            return formatted_articles

        except Exception as e:
            print(f"Error fetching news query: {e}")
            # Instead of returning an empty list, consider raising the exception
            # so the caller can handle it appropriately
            raise
