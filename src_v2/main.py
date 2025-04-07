# src_v2/main.py

from typing import Dict, Any, Optional
from src_v2.workflow.graph import create_workflow
from src_v2.memory.schema import GraphState
from src_v2.components.kg_builder.kg_builder import KnowledgeGraph
from src_v2.components.bias_analyzer.bias_agent import bias_analyzer_agent
from src_v2.components.fact_checker.fact_checker import fact_checker_agent


def initialize_state() -> GraphState:
    """Initialize a new graph state"""
    return GraphState(
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
        if 'bias_query' in input_data:
            initial_state.bias_query = input_data['bias_query']

    # Run workflow
    final_state = workflow.invoke(initial_state)
    return final_state


def process_direct_query(query: str, query_type: str = "fact_check") -> GraphState:
    """
    Process a direct query without using the full workflow.
    Direct interaction with the KG.

    Args:
        query: The query text
        query_type: Type of query ("fact_check" or "bias")

    Returns:
        Updated GraphState with results
    """
    # Initialize KG
    kg = KnowledgeGraph()

    # Create initial state
    state = initialize_state()

    # Set query based on type
    if query_type == "fact_check":
        state.news_query = query
        # Process with fact checker
        result_state = fact_checker_agent(state, kg)
    elif query_type == "bias":
        state.bias_query = query
        # Process with bias analyzer
        result_state = bias_analyzer_agent(state, kg)
    else:
        # Handle unknown query type
        state.error = f"Unknown query type: {query_type}"
        result_state = state

    return result_state


def fetch_and_analyze_news(topic: str = "politics", days: int = 1, limit: int = 10) -> GraphState:
    """
    Fetch news on a topic and analyze it directly with KG interaction

    Args:
        topic: News topic to search for
        days: Number of days to look back
        limit: Maximum number of articles to fetch

    Returns:
        GraphState with analyzed articles
    """
    # Initialize KG
    kg = KnowledgeGraph()

    # Fetch articles directly from KG builder
    articles = kg.fetch_news_articles(query=topic, days=days, limit=limit)

    # Create initial state with articles
    state = initialize_state()
    state.articles = articles

    # Process with bias analyzer
    bias_state = bias_analyzer_agent(state, kg)

    # Process with fact checker
    fact_state = fact_checker_agent(bias_state, kg)

    return fact_state


def process_results(state: GraphState) -> None:
    """Process and display results from the workflow"""
    if hasattr(state, 'articles') and state.articles:
        print(f"Processed {len(state.articles)} articles")

        for article in state.articles:
            print(f"\n--- Article: {article.get('title', 'Untitled')} ---")

            # Display bias analysis results
            if 'bias_analysis' in article and article['bias_analysis']:
                confidence = article['bias_analysis'].get('confidence_score', 0)
                assessment = article['bias_analysis'].get('overall_assessment', 'Unknown')

                print(f"Bias Analysis: {assessment} (Confidence: {confidence}%)")
                print("Bias Indicators:", article['bias_analysis'].get('findings', []))
            else:
                print("No bias analysis available")

            # Display fact-check results
            if 'fact_check' in article and article['fact_check']:
                report = article['fact_check'].get('report', {})
                verdict = report.get('overall_verdict', 'Unknown')

                print(f"Fact Check: {verdict}")

                if 'verified_claims' in article['fact_check']:
                    print("Verified claims:")
                    for claim in article['fact_check']['verified_claims']:
                        claim_verdict = claim.get('verification', {}).get('verdict', 'Unknown')
                        claim_text = claim.get('claim', 'Unknown claim')
                        print(f"- {claim_text}: {claim_verdict}")
            else:
                print("No fact-check available")

    elif hasattr(state, 'fact_check_result') and state.fact_check_result:
        print("\n--- Direct Fact Check Results ---")
        print(f"Status: {state.fact_check_result.get('status', 'Unknown')}")
        print(f"Overall verdict: {state.fact_check_result.get('report', {}).get('overall_verdict', 'Unknown')}")

        if 'verified_claims' in state.fact_check_result:
            print("\nVerified claims:")
            for claim in state.fact_check_result['verified_claims']:
                verdict = claim.get('verification', {}).get('verdict', 'Unknown')
                print(f"- {claim.get('claim', 'Unknown claim')}: {verdict}")

    elif hasattr(state, 'bias_analysis_result') and state.bias_analysis_result:
        print("\n--- Direct Bias Analysis Results ---")
        print(f"Overall Assessment: {state.bias_analysis_result.get('overall_assessment', 'Unknown')}")
        print(f"Confidence Score: {state.bias_analysis_result.get('confidence_score', 0)}%")

        print("\nFindings:")
        for finding in state.bias_analysis_result.get('findings', []):
            print(f"- {finding}")

    else:
        print("No results to display")
        if hasattr(state, 'error') and state.error:
            print(f"Error: {state.error}")


def main():
    """Main entry point with example usage"""
    print("News Analysis System with Direct KG Interaction")
    print("1. Process news through workflow")
    print("2. Direct fact-check query")
    print("3. Direct bias analysis query")
    print("4. Fetch and analyze news on a topic")

    choice = input("Select an option (1-4): ")

    if choice == "1":
        # Run the workflow with default settings
        final_state = run_workflow()
        process_results(final_state)

    elif choice == "2":
        query = input("Enter claim to fact-check: ")
        final_state = process_direct_query(query, "fact_check")
        process_results(final_state)

    elif choice == "3":
        query = input("Enter text to analyze for bias: ")
        final_state = process_direct_query(query, "bias")
        process_results(final_state)

    elif choice == "4":
        topic = input("Enter news topic (default: politics): ") or "politics"
        days = int(input("Number of days to look back (default: 1): ") or "1")
        limit = int(input("Maximum articles to fetch (default: 10): ") or "10")

        final_state = fetch_and_analyze_news(topic, days, limit)
        process_results(final_state)

    else:
        print("Invalid option selected")


if __name__ == "__main__":
    main()