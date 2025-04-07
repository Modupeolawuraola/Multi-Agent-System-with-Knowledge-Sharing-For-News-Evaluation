import os
from ...memory.schema import GraphState

from src.memory.knowledge_graph import KnowledgeGraph


def UpdaterAgent(state: GraphState) -> GraphState:
    """Agent for updating knowledge graph with new data"""
    new_state = state.copy()

    try:
        # Connect to real Neo4j
        kg = KnowledgeGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )

        # Get articles to add
        articles_to_add = state.articles if hasattr(state, "articles") else []

        # Add articles to KG
        for article in articles_to_add:
            kg.add_article(article)

        new_state.current_status = 'update_complete'
    except Exception as e:
        print(f"Error updating KG: {e}")
        new_state.current_status = 'update_failed'
        new_state.error = str(e)

    return new_state
