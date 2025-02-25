import requests
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv
from langchain_aws import BedrockChat
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

        #Initialize AWS Bedrock
        try:
            client = boto3.client("bedrock-runtime")
            self.llm= BedrockChat(
                client= client,
                model_id='anthropic.claude-3-sonnet-20240229-v1:0',
                model_kwargs= {"temperature":0.2}
            )

        except Exception as e:
            print(f" Error initializing Bedrock: {e}")
            self.llm= None



    def get_news_article(self, query:str, from_date: datetime=None) -> List[Dict]:
        """Fetch articles from NEWSAPI"""
        if from_date is None:
            from_date=datetime.now()- timedelta(days=1)

        #skip if LLM enhanced query not available
        if self.llm:
            try:
                pass
            except Exception as e:
                print(f"Error generating query:{e}")


            #fall back to the original query if LLM fails
        params={
            'q': query,
            'from': from_date.strftime('%Y-%m-%d'),
            'sortBy': 'publishedAt',
            'apiKey': self.api_key,
            'language': 'en'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            articles = response.json()['articles']

            #format article to match  schema
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
            return []

