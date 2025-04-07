WORKFLOW_CONFIG = {
    # Define the main collection and analysis flow
    "agent_connections": [
        # Main collection and analysis flow
        ("collector", "analyzer"),  # First: collect news
        ("analyzer", "updater"),  # Second: analyze and then update the KG
        ("updater", "retriever"),  # Third: retrieve from the updated KG
    ],

    # Define the independent paths
    "independent_paths": {
        # Direct fact-checking path (operates independently)
        "fact_check_path": ["fact_checker"],

        # Evaluation path (skips collector)
        "evaluation_path": ["analyzer", "updater", "retriever"]
    },

    # Define routing conditions
    "routing_conditions": {
        # Select path based on input
        "start": {
            "has_news_query": "fact_check_path",
            "has_articles_evaluation_mode": "evaluation_path",
            "default": "collection_path"
        }
    }
}

# Enable evaluation mode check in the workflow
ENABLE_EVALUATION_MODE_CHECK = True
