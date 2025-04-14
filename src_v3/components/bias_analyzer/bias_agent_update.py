import logging
import json
from src_v3.memory.schema import GraphState
from .tools import (create_bias_analysis_chain,
                    create_llm,
                    format_article,
                    initialize_entity_extractor,
                    extract_entities,
                    format_similar_articles)
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
                logging.info("No similar articles available. Use only the article text.")



            # Step 3: Query KG for similar articles
            # majority_bias = knowledge_graph.query_most_structurally_similar_bias(entities)
            # similar_context = f"The most similar article in the knowledge graph shares entities and has a bias of: {majority_bias}."
            #

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




    # # Check for bias query (direct analysis request) FIRST
    # if hasattr(graph_state, "bias_query") and graph_state.bias_query:
    #     logging.info(f"Processing direct bias query: {graph_state.bias_query}")
    #     try:
    #         # Create analysis chain for the query
    #         analysis_chain = create_bias_analysis_chain()
    #
    #         # Process the bias query directly
    #         query_result = analysis_chain.invoke({
    #             "content": graph_state.bias_query,
    #             "title": "Direct Query Analysis",
    #             "source": "User Query"
    #         })
    #
    #         # Set the result in the state
    #         new_state.bias_analysis_result = {
    #             "query": graph_state.bias_query,
    #             "analysis": query_result
    #         }
    #         new_state.current_status = 'bias_query_analyzed'
    #         logging.info("Direct bias query analysis completed")
    #         return new_state
    #     except Exception as e:
    #         logging.error(f"Error analyzing bias query: {str(e)}")
    #         new_state.error = str(e)
    #         new_state.current_status = 'bias_query_analysis_failed'
    #         return new_state
    #
    # # THEN check for empty articles list
    # if hasattr(graph_state, "articles") and graph_state.articles is not None:
    #     if len(graph_state.articles) == 0:
    #         logging.warning("Empty articles list provided")
    #         new_state.current_status = 'no_articles_to_analyze'
    #         return new_state
    #
    # # First check if articles are already in the state
    # articles_to_analyze = []
    # if hasattr(graph_state, "articles") and graph_state.articles and len(graph_state.articles) > 0:
    #     logging.info(f"Using {len(graph_state.articles)} articles from current state")
    #     articles_to_analyze = graph_state.articles
    #
    # # Otherwise get articles from the knowledge graph based on query
    # elif hasattr(graph_state, "news_query") and graph_state.news_query:
    #     # Retrieve articles from KG based on query
    #     # Check if retrieve_related_articles exists on the knowledge_graph (it might be a mock)
    #     if hasattr(knowledge_graph, "retrieve_related_articles"):
    #         articles_to_analyze = knowledge_graph.retrieve_related_articles(
    #             query=graph_state.news_query,
    #             limit=5
    #         )
    #         logging.info(f"Retrieved {len(articles_to_analyze)} articles from knowledge graph based on query")
    #     else:
    #         logging.warning("Knowledge graph does not have retrieve_related_articles method")
    #         new_state.current_status = 'kg_retrieval_not_supported'
    #         return new_state
    # else:
    #     logging.warning("No query provided for retrieving articles from knowledge graph")
    #     new_state.current_status = 'no_query_for_kg'
    #     return new_state
    #
    # # No articles found in knowledge graph
    # if not articles_to_analyze:
    #     logging.warning("No articles found in knowledge graph matching query")
    #     new_state.current_status = 'no_articles_found_in_kg'
    #     return new_state
    #
    # # making sure articles exist even if there is an error
    # try:
    #     # Create analysis chain
    #     analysis_chain = create_bias_analysis_chain()
    #
    #     # Analyze each article
    #     analyzed_articles = []
    #     for i, article in enumerate(articles_to_analyze):
    #         try:
    #             logging.info(
    #                 f"Analyzing article {i + 1}/{len(articles_to_analyze)}: {article.get('title', 'Untitled')}")
    #
    #             similar_context = []
    #             if hasattr(knowledge_graph, "get_similar_articles_by_embedding") and "url" in article:
    #                 similar_context = knowledge_graph.get_similar_articles_by_embedding(article["url"])
    #                 logging.info(f"Retrieved {len(similar_context)} similar articles using Node2Vec")
    #
    #             similar_articles_context = format_similar_articles(similar_context)
    #
    #             article_input = {
    #                 "article_text": article.get("full_content") or article.get("content", ""),
    #                 "similar_articles_context": similar_articles_context
    #             }
    #             # Format and analyze
    #             response = analysis_chain.invoke(article_input)
    #
    #             if isinstance(response, str):
    #                 result_data = json.loads(response)
    #             elif hasattr(response, "content"):
    #                 result_data = json.loads(response.content)
    #             else:
    #                 result_data = {}
    #
    #             # Update article with analysis
    #             article_copy = article.copy()
    #             article_copy['bias_analysis'] = result_data
    #             article_copy['predicted_bias'] = result_data.get("bias", "").lower()
    #             analyzed_articles.append(article_copy)
    #
    #             # Always call add_bias_analysis if it exists
    #             if hasattr(knowledge_graph, "add_bias_analysis"):
    #                 knowledge_graph.add_bias_analysis(article_copy)
    #                 logging.info(f"Successfully added bias analysis to knowledge graph: {article.get('title', 'Untitled')}")
    #             else:
    #                 logging.warning("Knowledge graph does not have add_bias_analysis method")
    #
    #             logging.info(f"Successfully analyzed article: {article.get('title', 'Untitled')}")
    #         except Exception as e:
    #             logging.error(f"Error analyzing article {article.get('title', 'Untitled')}: {str(e)}")
    #             article_copy = article.copy()
    #             article_copy['bias_analysis'] = {
    #                 'error': str(e),
    #                 'confidence_score': 0.0,
    #                 'findings': [],
    #                 'overall_assessment': 'Error during analysis',
    #                 'recommendations': []
    #             }
    #             analyzed_articles.append(article_copy)
    #
    #     # Update state with analyzed articles
    #     new_state.articles = analyzed_articles
    #     new_state.current_status = 'bias_analysis_complete'
    #     logging.info("Bias analysis completed successfully")
    #
    # except Exception as e:
    #     logging.error(f"Critical error in bias analysis: {str(e)}")
    #     # Preserve articles even on error
    #     if not hasattr(new_state, 'articles') or new_state.articles is None:
    #         new_state.articles = []
    #
    #     new_state.current_status = 'bias_analysis_failed'
    #     new_state.error = str(e)
    #
    # return new_state
    #
