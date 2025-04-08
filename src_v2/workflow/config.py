WORKFLOW_CONFIG = {
    # Define the simplified direct KG interaction flow
    "agent_connections": [
        # Direct interaction with KG
        ("kg_builder", "bias_analyzer"),  # First: build KG from news sources
        ("bias_analyzer", "fact_checker"),  # Second: analyze bias and fact-check
    ],

    # Define the independent paths
    "independent_paths": {
        # Direct fact-checking path (operates independently)
        "fact_check_path": ["fact_checker"],

        # Direct bias analysis path
        "bias_path": ["bias_analyzer"],

        #full processing path (default)
        "full_processing_path":["kg_builder", "bias_analyzer", "fact_checker"]
    },

    # Define routing conditions
    "routing_conditions": {
        # Select path based on input
        "start": {
            "has_news_query": "fact_check_path",
            "has_bias_query": "bias_path",
            "default": "full_processing_path"
        }
    }
}

# Enable evaluation mode check in the workflow
ENABLE_EVALUATION_MODE_CHECK = True