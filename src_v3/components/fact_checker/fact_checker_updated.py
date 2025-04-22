from typing import List, Dict, Any
from datetime import datetime
import json
from src_v3.memory.schema import GraphState
from .tools import (
    extract_entities_from_claim,
    create_factcheck_chain,
    parse_llm_response,
    transformer,
    initialize_entity_extractor,
    get_bedrock_llm
)
from src_v3.utils.aws_helpers import get_bedrock_llm
import logging

fact_check_chain = create_factcheck_chain()


def fact_checker_agent(state: GraphState, knowledge_graph, store_to_kg: bool = False) -> GraphState:
    """Update factchecker agent that directly interacts with the knowledge graph.
    Args:
        state: current system state
        knowledge_graph: knowledgeGraph instance for direct interaction
        store_to_kg: whether to store results in knowledge graph (default: False)
    """
    # Initialize transformer if needed
    global transformer
    if transformer is None:
        try:
            llm = get_bedrock_llm()
            initialize_entity_extractor(llm)
            logging.info("Initialized entity extractor in fact checker")
        except Exception as e:
            logging.warning(f"Could not initialize transformer: {e}")

    if isinstance(state, dict):
        state = GraphState(**state)

    new_state = state.copy()
    updated_articles = []

    # Handle direct query case
    if new_state.news_query and not new_state.articles:
        try:
            # Process direct query
            claim_text = new_state.news_query
            logging.info(f"Processing direct query: {claim_text}")

            # Extract entities
            entities = extract_entities_from_claim(claim_text)

            # Use KG to retrieve relevant context
            kg_context = ""
            if knowledge_graph:
                kg_context = knowledge_graph.retrieve_related_facts_text(entities)

            # Build input and run fact check chain
            input_vars = {
                "claim": claim_text,
                "related_kg_context": kg_context
            }
            response = fact_check_chain.invoke(input_vars)
            result = parse_llm_response(response.content)

            # Create a new article with the query and result
            new_article = {
                "title": f"Query: {claim_text[:50]}...",
                "content": claim_text,
                "source": "Direct Query",
                "date": datetime.now().isoformat(),
                "fact_check_result": result
            }
            updated_articles.append(new_article)

            # Only store in KG if explicitly requested
            if store_to_kg and knowledge_graph:
                try:
                    knowledge_graph.add_fact_check_result(
                        claim=claim_text,
                        result=response,
                        related_entities=entities
                    )
                except Exception as e:
                    logging.warning(f"Failed to store fact-check in KG: {e}")

        except Exception as e:
            logging.error(f"Error during direct query fact checking: {e}")
            new_article = {
                "title": f"Query: {new_state.news_query[:50]}...",
                "content": new_state.news_query,
                "source": "Direct Query",
                "date": datetime.now().isoformat(),
                "fact_check_result": {
                    "verdict": "False",
                    "confidence_score": 0,
                    "reasoning": f"Error encountered: {str(e)}",
                    "supporting_nodes": []
                }
            }
            updated_articles.append(new_article)

    # Process each article in the list
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
            response = fact_check_chain.invoke(input_vars)
            article["fact_check_result"] = parse_llm_response(response.content)

            # Only store in KG if explicitly requested
            if store_to_kg and knowledge_graph:
                try:
                    knowledge_graph.add_fact_check_result(
                        claim=claim_text,
                        result=response,
                        related_entities=entities
                    )
                except Exception as e:
                    logging.warning(f"Failed to store fact-check in KG: {e}")

        except Exception as e:
            logging.error(f"Error during fact checking: {e}")
            article["fact_check_result"] = {
                "verdict": "False",
                "confidence_score": 0,
                "reasoning": f"Error encountered: {str(e)}",
                "supporting_nodes": []
            }

        updated_articles.append(article)

    new_state.articles = updated_articles
    new_state.current_status = "fact_checked"
    return new_state