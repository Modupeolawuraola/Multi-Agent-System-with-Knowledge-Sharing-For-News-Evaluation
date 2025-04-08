import os
import sys
from typing import Dict, List, TypedDict, Optional

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the summarizer agent
from src_v2.agents import summarizer_agent, GraphState

def main():
    # Create a test graph state with proper typing
    test_state = {
        "articles": [
            {
                "url": "https://example.com/article1",
                "title": "Test Article 1",
                "content": "This is a test article about AI and its impact on society.",
                "source": "Test Source",
                "published_at": "2024-03-25"
            }
        ],
        "current_status": "initial",
        "error": None
    }
    
    # Run the summarizer agent
    try:
        result = summarizer_agent(test_state)
        print("Summarizer agent test successful!")
        print("Result:", result)
    except Exception as e:
        print("Error testing summarizer agent:", str(e))

if __name__ == "__main__":
    main() 