from workflow.graph import create_workflow
from memory.schema import GraphState

def initialize_state() -> GraphState:
    return GraphState(
        knowledge_graph={},
        article=[],
        current_article=None,
        bias_results=[],
        current_status="ready"
    )

def main():
    #create workflow
    workflow =create_workflow()

    #initialize state
    initial_state=initialize_state()

    #run workflow
    final_state= workflow.run(initial_state)

    #process results
    for article in final_state['articles']:
        if article['bias_analysis']['is_biased']:
            print(f"Biased article found: {article['title']}")
            print("Bias Indicators:", article['bias_analysis']['bias_indicators'])
        else:
            print(f"Unbiased articles: {article['title']}")

if __name__=="__main__":
    main()
