import os
import re
import requests
import logging
import json
from typing import List, Dict, Any
import boto3
from langchain_aws import ChatBedrock
from dotenv import load_dotenv
from datetime import datetime, timedelta
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from src_v3.components.fact_checker.fc_prompt import FactCheckPromptWithKG
from langchain.chains import LLMChain

load_dotenv()

transformer = None

def get_bedrock_llm():
    """Initialize and return a Bedrock LLM client."""
    # Always use real AWS Bedrock
    print("Using real AWS Bedrock")
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    llm = ChatBedrock(
        client=client,
        model_id='anthropic.claude-3-5-sonnet-20240620-v1:0',
        model_kwargs={"temperature": 0.2}
    )
    return llm


def initialize_entity_extractor(llm) -> None:
    """Initialize the LLMGraphTransformer for entity extraction"""
    global transformer
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=[
            "Person", "Organization", "Event", "Policy", "Issue", "Location",
            "Election", "Bill", "Vote", "Speech", "Alliance"
        ],
        allowed_relationships=[
            "published_by", "has_bias","fact_checked_by", "mentions",
            "affiliated_with", "participated_in", "endorsed",  "sponsored",
            "gave_speech", "involved_in", "organized",  "supports",
            "lobbied_for", "takes_place_in", "addresses",  "focuses_on",
            "decided_by", "includes", "subject_of"
        ]
    )


def extract_entities_from_claim(claim_text: str) -> List[str]:
    """Extracts named entities from article content using LLM-based graph transformation."""
    logging.info(f"Extracting entities from claim text (length: {len(claim_text)})")
    global transformer

    if transformer is None:
        raise RuntimeError("Transformer not initialized. Call initialize_entity_extractor(llm) first.")

    doc = Document(page_content=claim_text)
    graph_objs = transformer.convert_to_graph_documents([doc])
    entities = []
    for graph in graph_objs:
        # logging.info(f"GraphDoc Nodes: {graph.nodes}")
        for node in graph.nodes:
            name = node.properties.get("name") or node.id
            if name:
                entities.append(name)

    entities = list(set([e.strip() for e in entities if e.strip()]))
    logging.info(f"Extracted entities: {entities}")
    return list(set(entities))

_factcheck_chain = None
def create_factcheck_chain():
    """fact-checking chain with KG context"""
    global _factcheck_chain
    if _factcheck_chain is None:
        try:
            llm = get_bedrock_llm()
            _factcheck_chain = FactCheckPromptWithKG | llm
        except Exception as e:
            print(f"Error creating fact-checking chain: {e}")
            raise
    return _factcheck_chain

def parse_llm_response(response_content: str) -> dict:
    try:
        return json.loads(response_content)
    except json.JSONDecodeError:
        try:
            match = re.search(r"\{[\s\S]*\}", response_content)
            if match:
                return json.loads(match.group(0))
            else:
                raise ValueError("No JSON object found in response")
        except Exception as e:
            logging.error(f"Failed to extract JSON: {e}")
            return {
                "verdict": "Unknown",
                "confidence_score": 0,
                "reasoning": f"Failed to parse LLM response: {str(e)}",
                "supporting_nodes": []
            }


class FactCheckTools:
    """Tools for fact-checking news articles."""

    def __init__(self, knowledge_graph=None):
        """Initialize the fact-checking tools."""
        self.search_api_key = os.environ.get('SEARCH_API_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        self.knowledge_base_api_key = os.environ.get('KNOWLEDGE_BASE_API_KEY')
        self.knowledge_graph = knowledge_graph

        # Initialize LLM for query generation
        self.llm = get_bedrock_llm()

    def search_knowledge_graph(self, claim: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge graph for evidence related to a claim.

        Args:
            claim: The factual claim to verify
            limit: Maximum number of results to return

        Returns:
            List of evidence items from the knowledge graph
        """
        if not self.knowledge_graph:
            return []

        try:
            # Query the knowledge graph for related information
            results = self.knowledge_graph.retrieve_related_articles(query=claim, limit=limit)

            evidence = []
            for result in results:
                # Format each result from the KG as evidence
                evidence.append({
                    "source": "knowledge_graph",
                    "title": result.get("a.title", ""),
                    "content": result.get("a.full_content", ""),
                    "url": result.get("a.url", ""),
                    "date_published": result.get("a.publishedAt", ""),
                    "date_retrieved": datetime.now().isoformat(),
                    "source_name": result.get("a.source_name", ""),
                    "source_credibility": self._check_source_credibility(result.get("a.source_name", "")),
                    "source_type": "Knowledge_graph"
                })
            return evidence
        except Exception as e:
            print(f"Error searching knowledge graph: {e}")
            return []

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

    def store_fact_check_in_kg(self, claim: str, verification_result: Dict) -> bool:
        """
        Store the fact check result in the knowledge graph.

        Args:
            claim: The verified claim
            verification_result: The verification result with evidence

        Returns:
            Boolean indicating success
        """
        if not self.knowledge_graph:
            return False

        try:
            # Create a pseudo-article structure to fit the KG's add_fact_check method
            fact_check_entry = {
                "url": f"fact-check://{datetime.now().strftime('%Y%m%d%H%M%S')}/{hash(claim)}",
                "title": f"Fact Check: {claim[:50]}...",
                "content": claim,
                "source": "Fact Checking System",
                "date": datetime.now().isoformat(),
                "fact_check": {
                    "verified_claims": [
                        {
                            "claim": claim,
                            "verification": verification_result
                        }
                    ],
                    "report": {
                        "overall_verdict": verification_result.get("verdict", "unknown"),
                        "overall_accuracy": verification_result.get("confidence", 0.5)
                    }
                }
            }

            # Add to knowledge graph
            result = self.knowledge_graph.add_article(fact_check_entry)
            return result
        except Exception as e:
            print(f"Error storing fact check in knowledge graph: {e}")
            return False

