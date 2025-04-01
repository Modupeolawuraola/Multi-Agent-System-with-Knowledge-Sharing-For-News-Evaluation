WORKFLOW_CONFIG = {
    "agent_connections": [
        ("collector", "analyzer"),   # First: collect news
        ("analyzer", "updater"),     # Second: analyze and then update
        ("updater", "retriever"),    # Third: update then retrieve
    ]
}