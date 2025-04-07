import os
import json
from dotenv import load_dotenv
import requests
from newspaper import Article
from datetime import datetime, timedelta


load_status = load_dotenv('.env')
if load_status is False:
    raise RuntimeError('Environment variables not loaded.')

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
NEWS_API_URL = os.getenv('NEWS_API_URL')

def get_news_json_from_api(api_url, api_key, country="us", output_file=None, max_results=10):
    params = {
        "apikey": api_key,
        "category": "politics",
        "country": country,
        "count": max_results,
        "sortBy": "publishedAt"  # Prioritizes latest news
    }

    try:
        # Send request to News API
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Handle HTTP errors
        news_data = response.json()

        articles = news_data.get("articles", [])

        full_articles = []
        for article in articles:
            url = article.get("url")
            if not url:
                continue

            try:
                # Scrape full text
                news_article = Article(url)
                news_article.download()
                news_article.parse()

                article["full_content"] = news_article.text
                full_articles.append(article)
                print(f"Scraped full article: {article.get('title')}")
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")

        # Generate a timestamped filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"political_news_{timestamp}.json"

        # Save JSON data to a file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(news_data, f, indent=4)

        print(f"Political news articles saved to {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")


get_news_json_from_api(NEWS_API_URL, NEWS_API_KEY)