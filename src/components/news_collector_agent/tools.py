import requests
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI


load_dotenv()
from .news_prompt import (
query_generation_prompt,
article_filter_prompt,
source_validation_prompt
)

class NewsAPI:
    def __init__(self):
        self.api_key = os.environ.get('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"
        self.llm= ChatOpenAI(temperature=0)

    def get_news_article(self, query:str, from_date: datetime=None) -> List[Dict]:
        """Fetch articles from NEWSAPI"""
        if from_date is None:
            from_date=datetime.now()-timedelta(days=1)

        #generate optimized search queries using llm
        try:
            chain=query_generation_prompt | self.llm
            enhanced_queries = chain.invoke({"topic": query}).content.split('\n')
            query =" OR ".join(enhanced_queries) #comibing queries for the api
        except Exception as e:
            print(f"Error generating query: {e}")

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
                formatted_articles= {
                    'title': article.get('title'),
                    'content': article.get('content'),
                    'source': article.get('source', {}).get('name'),
                    'date': article.get('publishedAt'),
                    'url': article.get('url'),
                    'bias_analysis': None
                }

                #validate article relevance using llm
                try:
                    chain= article_filter_prompt | self.llm
                    validation_result = chain.invoke({"topic": query,
                                                      "title": formatted_articles['title'],
                                                      "summary": formatted_articles['content'][:200], #for the first 200 characters
                                                      "source": formatted_articles['source']
                                                      })

                    if validation_result.content.get('is_relevant', True):
                        formatted_articles.append(formatted_articles)
                except Exception as e:
                    print(f"Error generating query: {e}")
                    formatted_articles.append(formatted_articles) #include if articles fails
                return formatted_articles

        except Exception as e:
            print(f"Error fetching news query: {e}")
            return []

    def validation_source(self, source_name: str) -> Dict:
        """Validate credibility of news source"""
        try:
            chain= source_validation_prompt | self.llm
            result = chain.invoke({'source_name' : source_name})
            return result.content
        except Exception as e:
            print(f"Error validating source: {e}")
            return {"credibility_score": 0.5, "recommendation": "verify"}

    @staticmethod
    def format_date(date_str:str) -> datetime:
        """convert date string to datetime object"""
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))


