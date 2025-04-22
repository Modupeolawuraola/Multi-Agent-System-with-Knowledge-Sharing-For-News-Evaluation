import logging
import json
from src_v3.memory.schema import GraphState
from .tools import (
    create_bias_analysis_chain,
    create_llm,
    format_article,
    initialize_entity_extractor,
    extract_entities,
    transformer
)
from src_v3.utils.aws_helpers import diagnostic_check
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bias_analyzer.log"),
        logging.StreamHandler()
    ]
)


def bias_analyzer_agent(graph_state: GraphState, knowledge_graph) -> GraphState:
    """
    Bias analysis agent that uses LLM to analyze articles with KG context.

    Args:
        graph_state: Current system state
        knowledge_graph: Neo4j knowledge graph instance

    Returns:
        Updated graph state
    """
    # Initialize transformer if needed
    global transformer
    if transformer is None:
        try:
            llm = create_llm()
            initialize_entity_extractor(llm)
            logging.info("Initialized entity extractor in bias analyzer")
        except Exception as e:
            logging.warning(f"Could not initialize transformer: {e}")

    # Only run diagnostic check if we're NOT in evaluation mode
    if os.environ.get("EVALUATION_MODE", "false").lower() != "true":
        diagnostic_check()
        llm = create_llm()
        initialize_entity_extractor(llm)

    logging.info("Starting direct KG bias analysis")

    if isinstance(graph_state, dict):
        graph_state = GraphState(**graph_state)

    new_state = graph_state.copy()

    analysis_chain = create_bias_analysis_chain()
    analyzed_articles = []

    for article in graph_state.articles:
        try:
            logging.info("Analyzing article: %s", article.get("title", "Untitled"))

            # Step 1: Format main article
            article_text = format_article(article)

            # Step 2: Extract entities
            if knowledge_graph is not None:
                entities = extract_entities(article)
                entities_str = ", ".join(entities)
                most_similar_bias = knowledge_graph.query_most_structurally_similar_bias(entities)
                similar_context = f"The most similar article in the political news KG has bias: {most_similar_bias}."
                logging.info("Extracted entities: %s", entities)
                logging.info("Most similar bias: %s", most_similar_bias)
            else:
                similar_context = "No similar articles available. Use only the article text."
                most_similar_bias = "Unknown"
                entities_str = "N/A"
                logging.info("No similar articles available. Use only the article text.")

            # Step 5: Invoke LLM with both article and context
            result = analysis_chain.invoke({
                "article_text": article_text,
                "similar_bias": most_similar_bias,
                "matched_entities": entities_str
            })

            logging.info("LLM bias result: %s", result)

            # Update article with result
            article_copy = article.copy()
            article_copy["bias_result"] = result
            analyzed_articles.append(article_copy)

        except Exception as e:
            logging.error("Error processing article '%s': %s", article.get("title", "Untitled"), e)

    new_state.articles = analyzed_articles
    new_state.current_status = "bias_analyzed"
    return new_state