import os
import requests
import json
from typing import List, Dict, Any
import boto3
from langchain_aws import ChatBedrock
from dotenv import load_dotenv
import wikipedia
from datetime import datetime, timedelta

load_dotenv()


def get_bedrock_llm():
    """Initialize and return a Bedrock LLM client."""
    # Always use real AWS Bedrock
    print("Using real AWS Bedrock")
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    llm = ChatBedrock(
        client=client,
        model_id='anthropic.claude-3-sonnet-20240229-v1:0',
        model_kwargs={"temperature": 0.2}
    )
    return llm


class FactCheckTools:
    """Tools for fact-checking news articles."""

    def __init__(self):
        """Initialize the fact-checking tools."""
        self.search_api_key = os.environ.get('SEARCH_API_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        self.knowledge_base_api_key = os.environ.get('KNOWLEDGE_BASE_API_KEY')

        # Initialize LLM for query generation
        self.llm = get_bedrock_llm()

    def search_for_evidence(self, claim: str, num_sources: int = 5) -> List[Dict[str, Any]]:
        """
        Search for evidence related to a claim using multiple sources.

        Args:
            claim: The factual claim to verify
            num_sources: Number of sources to search for evidence

        Returns:
            List of evidence items with source metadata
        """
        evidence = []

        # Try multiple evidence sources
        web_evidence = self.search_web(claim, max_results=num_sources)
        evidence.extend(web_evidence)

        # Search dedicated fact-checking sites
        fact_check_evidence = self.search_fact_check_sites(claim)
        evidence.extend(fact_check_evidence)

        wikipedia_evidence = self.search_wikipedia(claim)
        if wikipedia_evidence:
            evidence.extend(wikipedia_evidence)

        # Search recent news if claim seems current
        if self._is_likely_recent_claim(claim):
            news_evidence = self.search_recent_news(claim, max_results=3)
            evidence.extend(news_evidence)

        return evidence

    def search_web(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Search the web for evidence using a search API.

        Args:
            query: Search query related to the claim
            max_results: Maximum number of results to return

        Returns:
            List of web search results with metadata
        """
        # Use SerpAPI or similar if available
        if self.search_api_key:
            try:
                # Example with SerpAPI
                params = {
                    "q": query,
                    "api_key": self.search_api_key,
                    "num": max_results
                }
                response = requests.get(
                    "https://serpapi.com/search",
                    params=params
                )
                response.raise_for_status()

                results = response.json().get("organic_results", [])
                return [
                    {
                        "source": "web_search",
                        "title": result.get("title", ""),
                        "content": result.get("snippet", ""),
                        "url": result.get("link", ""),
                        "date_retrieved": datetime.now().isoformat(),
                        "source_name": self._extract_domain(result.get("link", "")),
                        "source_credibility": self._check_source_credibility(
                            self._extract_domain(result.get("link", "")))
                    }
                    for result in results[:max_results]
                ]
            except Exception as e:
                print(f"Error searching web: {e}")
                return []

        # If no API is available, use LLM to generate search queries
        # Use the real LLM to generate realistic queries
        system_message = f"""Generate {max_results} search queries to verify this claim: "{query}"
        The queries should be designed to find reliable information that can confirm or refute the claim.
        Return ONLY a JSON array of queries, for example:
        ["query 1", "query 2", "query 3"]
        """

        try:
            response = self.llm.invoke(system_message)
            queries = json.loads(response.content)

            return [
                {
                    "source": "search_query",
                    "title": f"Search query for verification",
                    "content": f"Suggested search query: {q}",
                    "date_retrieved": datetime.now().isoformat(),
                    "source_name": "AI Assistant",
                    "source_credibility": 0.5,
                    "query": q
                }
                for q in queries[:max_results]
            ]
        except Exception as e:
            print(f"Error generating search queries: {e}")
            return []

    def search_fact_check_sites(self, query: str) -> List[Dict[str, Any]]:
        """
        Search dedicated fact-checking websites.

        Args:
            query: Search query related to the claim

        Returns:
            List of fact-checking results with metadata
        """
        fact_check_sites = [
            "factcheck.org",
            "politifact.com",
            "snopes.com",
            "apnews.com/hub/ap-fact-check",
            "reuters.com/fact-check"
        ]

        evidence = []

        if self.search_api_key:
            # For each fact check site, search for relevant fact checks
            for site in fact_check_sites:
                try:
                    # Use your search API with site-specific search
                    params = {
                        "q": f"site:{site} {query}",
                        "api_key": self.search_api_key,
                        "num": 2
                    }
                    response = requests.get(
                        "https://serpapi.com/search",
                        params=params
                    )
                    response.raise_for_status()

                    results = response.json().get("organic_results", [])
                    for result in results[:2]:
                        evidence.append({
                            "source": "fact_checker",
                            "title": result.get("title", ""),
                            "content": result.get("snippet", ""),
                            "url": result.get("link", ""),
                            "date_retrieved": datetime.now().isoformat(),
                            "source_name": site,
                            "source_credibility": 0.9,  # Higher credibility for fact-checking sites
                            "source_type": "fact_checker"
                        })
                except Exception as e:
                    print(f"Error searching {site}: {e}")
        else:
            # If we don't have a search API, suggest fact-checking websites to check
            for site in fact_check_sites:
                evidence.append({
                    "source": "fact_checker_suggestion",
                    "title": f"Suggested fact-check source",
                    "content": f"This claim should be verified on {site}",
                    "url": f"https://{site}",
                    "date_retrieved": datetime.now().isoformat(),
                    "source_name": site,
                    "source_credibility": 0.9,
                    "source_type": "fact_checker_suggestion"
                })

        return evidence

    def search_wikipedia(self, query: str, max_results: int = 2) -> List[Dict[str, Any]]:
        """
        Search Wikipedia for relevant information.

        Args:
            query: Search query related to the claim
            max_results: Maximum number of results to return

        Returns:
            List of Wikipedia search results with metadata
        """
        try:
            # Search Wikipedia
            search_results = wikipedia.search(query, results=max_results)

            evidence = []
            for title in search_results:
                try:
                    # Get page summary
                    page = wikipedia.page(title)
                    evidence.append({
                        "source": "wikipedia",
                        "title": page.title,
                        "content": page.summary[:1000],  # Limit to first 1000 chars
                        "url": page.url,
                        "date_retrieved": datetime.now().isoformat(),
                        "source_name": "Wikipedia",
                        "source_credibility": 0.8,  # Wikipedia has generally good but not perfect credibility
                        "source_type": "encyclopedia"
                    })
                except Exception as e:
                    print(f"Error getting Wikipedia page {title}: {e}")

            return evidence
        except Exception as e:
            print(f"Error searching Wikipedia: {e}")
            return []

    def search_recent_news(self, query: str, max_results: int = 2) -> List[Dict[str, Any]]:
        """
        Search recent news articles for evidence.

        Args:
            query: Search query related to the claim
            max_results: Maximum number of results to return

        Returns:
            List of recent news results with metadata
        """
        if self.news_api_key:
            try:
                # Use NewsAPI
                params = {
                    "q": query,
                    "apiKey": self.news_api_key,
                    "language": "en",
                    "sortBy": "relevancy",
                    "pageSize": max_results
                }
                response = requests.get(
                    "https://newsapi.org/v2/everything",
                    params=params
                )
                response.raise_for_status()

                articles = response.json().get("articles", [])
                return [
                    {
                        "source": "recent_news",
                        "title": article.get("title", ""),
                        "content": article.get("description", "") + "\n" + (article.get("content", "") or ""),
                        "url": article.get("url", ""),
                        "date_published": article.get("publishedAt", ""),
                        "date_retrieved": datetime.now().isoformat(),
                        "source_name": article.get("source", {}).get("name", ""),
                        "source_credibility": self._check_source_credibility(article.get("source", {}).get("name", "")),
                        "source_type": "news_outlet"
                    }
                    for article in articles[:max_results]
                ]
            except Exception as e:
                print(f"Error searching recent news: {e}")
                return []

        return []

    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace("www.", "")
        except:
            return url

    def _check_source_credibility(self, source_name: str) -> float:
        """
        Check the credibility of a source.

        Args:
            source_name: Name of the source

        Returns:
            Credibility score from 0.0 to 1.0
        """
        # In a real implementation, this would check against a database of source ratings
        # For now, we'll use a simple heuristic based on known reliable sources

        # Expanded list of sources with credibility ratings
        reliable_sources = {
            # Top-tier news agencies
            "reuters.com": 0.95,
            "apnews.com": 0.95,
            "bloomberg.com": 0.85,

            # Public broadcasters
            "bbc.com": 0.9,
            "bbc.co.uk": 0.9,
            "npr.org": 0.85,
            "pbs.org": 0.85,

            # Major newspapers
            "nytimes.com": 0.85,
            "wsj.com": 0.85,
            "washingtonpost.com": 0.85,
            "ft.com": 0.85,  # Financial Times
            "economist.com": 0.9,

            # Fact-checking sites
            "factcheck.org": 0.95,
            "snopes.com": 0.9,
            "politifact.com": 0.9,

            # Scientific sources
            "nature.com": 0.95,
            "science.org": 0.95,
            "scientificamerican.com": 0.9,
            "smithsonianmag.com": 0.85,
            "nationalgeographic.com": 0.85,

            # Research institutions
            "pewresearch.org": 0.95,
            "who.int": 0.95,  # World Health Organization
            "cdc.gov": 0.95,  # CDC
            "nih.gov": 0.95,  # NIH
            "worldbank.org": 0.9,

            # Lower credibility sources
            "buzzfeed.com": 0.5,
            "dailymail.co.uk": 0.4,
            "nypost.com": 0.5,

            # Social media - generally low credibility as sources
            "twitter.com": 0.3,
            "facebook.com": 0.3,
            "instagram.com": 0.3,
            "tiktok.com": 0.3,
            "reddit.com": 0.4
        }

        # Look for the domain in our list
        for domain, score in reliable_sources.items():
            if domain in source_name.lower():
                return score

        # Default credibility for unknown sources
        return 0.5

    def _is_likely_recent_claim(self, claim: str) -> bool:
        """
        Determine if a claim is likely about recent events.

        Args:
            claim: The claim to check

        Returns:
            Boolean indicating if claim likely refers to recent events
        """
        # Check for temporal indicators in the claim
        recent_indicators = [
            "yesterday", "today", "this week", "this month", "this year",
            "latest", "recent", "just announced", "breaking", "now",
            "currently", "ongoing", "developing"
        ]

        claim_lower = claim.lower()
        for indicator in recent_indicators:
            if indicator in claim_lower:
                return True

        # Check for current year and month
        current_year = str(datetime.now().year)
        if current_year in claim:
            return True

        # Check for current month name
        current_month = datetime.now().strftime("%B")  # Full month name
        if current_month in claim or current_month.lower() in claim_lower:
            return True

        return False
