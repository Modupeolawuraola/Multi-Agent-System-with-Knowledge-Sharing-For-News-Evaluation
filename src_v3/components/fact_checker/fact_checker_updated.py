from typing import List, Dict, Any
from datetime import datetime
import json
from src_v3.memory.schema import GraphState
from .tools import (
    extract_entities_from_claim,
    create_factcheck_chain,
    parse_llm_response
    )
from src_v3.utils.aws_helpers import get_bedrock_llm
import logging

fact_check_chain = create_factcheck_chain()

def fact_checker_agent(state: GraphState, knowledge_graph, store_to_kg: bool = True) -> GraphState:
    """Update factchecker agent that directly interacts with the knowledge graph.
    Args:
        state:current system state
        knowledge_graph:knowledgeGraph instance for direct interaction
        """
    if isinstance(state, dict):
        state = GraphState(**state)

    new_state = state.copy()
    updated_articles = []

    for article in new_state.articles:
        if isinstance(article, str):
            try:
                article = json.loads(article)
            except Exception as e:
                logging.error(f"Skipping string article, failed to parse JSON: {e}")
                continue

        if not isinstance(article, dict):
            logging.error(f"Invalid article type: {type(article)} — skipping")
            continue

        claim_text = article.get("claim") or article.get("content") or article.get("full_content", "")
        if not claim_text:
            article['fact_check_result'] = {"error": "No claim or content provided"}
            updated_articles.append(article)
            continue

        try:
            # Step 1: Extract entities
            entities = extract_entities_from_claim(claim_text)

            # Step 2: Use KG to retrieve relevant context
            kg_context = ""
            if knowledge_graph:
                kg_context = knowledge_graph.retrieve_related_facts_text(entities)

            # Step 3: Build input and run the fact check chain
            input_vars = {
                "claim": claim_text,
                "related_kg_context": kg_context
            }
            # result = fact_check_chain.invoke(input_vars)
            # article["fact_check_result"] = result
            response = fact_check_chain.invoke(input_vars)
            article["fact_check_result"] = parse_llm_response(response.content)

        except Exception as e:

            logging.error(f"Error during fact checking: {e}")
            article["fact_check_result"] = {
                "verdict": "False",
                "confidence_score": 0,
                "reasoning": f"Error encountered: {str(e)}",
                "supporting_nodes": []
            }

        if store_to_kg and knowledge_graph:
            try:
                knowledge_graph.add_fact_check_result(
                    claim=claim_text,
                    result=result,
                    related_entities=entities
                )
            except Exception as e:
                logging.warning(f"Failed to store fact-check in KG: {e}")

        updated_articles.append(article)

    new_state.articles = updated_articles
    new_state.current_status = "fact_checked"
    return new_state



