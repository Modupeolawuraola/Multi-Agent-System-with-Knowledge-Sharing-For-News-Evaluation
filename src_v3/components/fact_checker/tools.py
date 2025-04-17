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