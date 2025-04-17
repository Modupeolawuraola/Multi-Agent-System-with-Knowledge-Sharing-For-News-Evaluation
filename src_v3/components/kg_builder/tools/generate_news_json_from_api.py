
import os
import json
from dotenv import load_dotenv
import requests
from newspaper import Article
from datetime import datetime, timedelta, date
from newsapi import NewsApiClient
from bs4 import BeautifulSoup



# env_path = os.path.join('../..', '.env')
# load_status = load_dotenv(env_path)
# if load_status is False:
#     raise RuntimeError('Environment variables not loaded.')

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
NEWS_API_URL = os.getenv('NEWS_API_URL')
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def get_news_json_from_api(api_url, api_key,date, output_file=None, max_results=100):
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    try:
        response = newsapi.get_everything(
            q="US politics",  # Ensure it's a string
            from_param=date,
            to=date,
            page_size=max_results,
            sources="abc-news,associated-press,axios,breitbart-news,cbs-news,cnn,fox-news,msnbc,national-review,nbc-news,newsweek,new-york-magazine,politico,reuters,the-american-conservative,the-hill,the-huffington-post,the-washington-post,the-washington-times,usa-today",
            language="en",
            sort_by="publishedAt"
        )
        # Send request to News API
        # response.raise_for_status()  # Handle HTTP errors
        # news_data = response.json()

        articles = response.get("articles", [])

        full_articles = []
        for article in articles:
            url = article.get("url")
            if not url:
                continue

            print(f"Scraping: {url}")
            content = scrape_with_fallback(url)

            if content and len(content.strip()) > 100:
                article["full_content"] = content
                full_articles.append(article)
                print(f"✅ Scraped: {article.get('title')}")
            else:
                print(f"⚠️ Empty or short content from {url}")
            # try:
            #     # Scrape full text
            #     news_article = Article(url)
            #     news_article.download()
            #     news_article.parse()
            #
            #     article["full_content"] = news_article.text
            #     full_articles.append(article)
            #     print(f"Scraped full article: {article.get('title')}")
            # except Exception as e:
            #     print(f"Failed to scrape {url}: {e}")

        # Generate a timestamped filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"political_news_{date}.json"

        # Save JSON data to a file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4)

        print(f"Political news articles saved to {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")

def get_dates_between(start_date_str, end_date_str):
    """
    Generates a list of dates (as strings in YYYY-MM-DD format) between two dates (inclusive).

    Args:
        start_date_str (str): Start date in YYYY-MM-DD format.
        end_date_str (str): End date in YYYY-MM-DD format.

    Returns:
        list: List of dates as strings.
    """
    start_date = date.fromisoformat(start_date_str)
    end_date = date.fromisoformat(end_date_str)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    return dates

def scrape_with_fallback(url):
    try:
        # First try newspaper3k
        article = Article(url)
        article.download()
        article.parse()
        if len(article.text.strip()) > 100:
            return article.text
    except Exception as e:
        print(f"[newspaper3k failed] {url}: {e}")

    try:
        # Use custom scraper for known domains
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(response.text, "html.parser")

        if "foxnews.com" in url:
            paragraphs = soup.select("div.article-body p, article p")
            return "\n".join(p.get_text() for p in paragraphs)

        elif "newsweek.com" in url:
            paragraphs = soup.select("div.article-body p, div.article-content p")
            return "\n".join(p.get_text() for p in paragraphs)

        else:
            # Generic fallback
            paragraphs = soup.find_all("p")
            return "\n".join(p.get_text() for p in paragraphs)

    except Exception as e:
        print(f"[fallback failed] {url}: {e}")
        return None

# start_date_str = "2025-03-25"
# end_date_str = "2025-03-31"
# date_list = get_dates_between(start_date_str, end_date_str)
#
# for date_str in date_list:
#     get_news_json_from_api(NEWS_API_URL, NEWS_API_KEY, date=date_str)