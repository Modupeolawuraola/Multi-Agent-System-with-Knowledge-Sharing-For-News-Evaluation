from typing import Dict, Any
from src.workflow.graph import create_workflow
from src.memory.schema import GraphState


def initialize_state() -> GraphState:
    return GraphState(
        knowledge_graph={"articles": []},  # Initialize with empty articles list
        articles=[],
        current_status="ready"
    )


def run_workflow(input_data: Dict[str, Any] = None) -> GraphState:
    """Run the workflow with optional input data"""
    # Create workflow
    workflow = create_workflow()

    # Initialize state
    initial_state = initialize_state()

    # Add any input data to the initial state
    if input_data:
        if 'articles' in input_data:
            initial_state.articles = input_data['articles']
        if 'news_query' in input_data:
            initial_state.news_query = input_data['news_query']

    # Run workflow
    final_state = workflow.invoke(initial_state)
    return final_state


def process_results(state: GraphState) -> None:
    """Process and display results from the workflow"""
    if hasattr(state, 'articles') and state.articles:
        for article in state.articles:
            if 'bias_analysis' in article and article['bias_analysis']:
                confidence = article['bias_analysis'].get('confidence_score', 0)
                if confidence > 50:
                    print(f"Biased article found: {article.get('title', 'Untitled')}")
                    print("Bias Indicators:", article['bias_analysis'].get('findings', []))
                else:
                    print(f"Unbiased article: {article.get('title', 'Untitled')}")
            else:
                print(f"Article without bias analysis: {article.get('title', 'Untitled')}")

    elif hasattr(state, 'fact_check_result') and state.fact_check_result:
        print("Fact check results:")
        print(f"Status: {state.fact_check_result.get('status', 'Unknown')}")
        print(f"Overall verdict: {state.fact_check_result.get('report', {}).get('overall_verdict', 'Unknown')}")

        if 'verified_claims' in state.fact_check_result:
            print("\nVerified claims:")
            for claim in state.fact_check_result['verified_claims']:
                verdict = claim.get('verification', {}).get('verdict', 'Unknown')
                print(f"- {claim.get('claim', 'Unknown claim')}: {verdict}")
    else:
        print("No results to display")


def main():
    # Run the workflow with default settings
    final_state = run_workflow()

    # Process and display results
    process_results(final_state)


if __name__ == "__main__":
    main()
