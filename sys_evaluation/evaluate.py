import time
import json
import sys
import os
import logging
from src.utils.aws_helpers import diagnostic_check

# Adding the root directory to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from src_v2.memory.schema import GraphState
# Import real KG instead of mock
from src_v2.memory.knowledge_graph import KnowledgeGraph  # Assuming this is the correct import
from sys_evaluation.metrics import calculate_accuracy, calculate_bias_precision_recall
from sys_evaluation.visualization_evaluate import generate_evaluation_chart
from src_v2.workflow.simplified_workflow import process_articles
# Import for direct query route
from src_v2.components.fact_checker.fact_checker_Agent import FactCheckerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("evaluation.log"),
        logging.StreamHandler()
    ]
)


def load_test_dataset():
    """Loading pre-labeled test articles"""
    import pandas as pd

    # Load from CSV file
    df = pd.read_csv('./test_dataset/test_bias_4_01_to_4_05.csv')

    # Convert DataFrame rows to article dictionaries
    test_articles = []
    for _, row in df.iterrows():
        article = {
            "title": row['title'],
            "content": row['full_content'],
            "source": row['source_name'],
            "date": row['publishedAt'],
            "url": row['url'],
            # Ground truth labels for evaluation
            'ground_truth_bias': row['bias']
            # 'ground_truth_facts': json.loads(row['fact_claims'])  # List of true/false claims
        }
        test_articles.append(article)
    return test_articles


def load_politifact_dataset():
    """Load PolitiFact dataset for fact checking evaluation"""
    import pandas as pd

    # Load from CSV file
    df = pd.read_csv('./test_dataset/mbfc_fact_checks.csv')

    test_claims = []
    for _, row in df.iterrows():
        claim = {
            "claim": row['claim'],
            "date": row['date'],
            "ground_truth_verdict": row['rating']  # true, false, pants-fire, etc.
        }
        test_claims.append(claim)
    return test_claims


def evaluate_news_analysis_workflow():
    """Evaluation using the simplified workflow with actual components"""
    # Run diagnostic check
    print("Running AWS credential diagnostic test")
    diagnostic_check()

    # Create real knowledge graph
    real_kg = KnowledgeGraph()

    # Load test data
    test_dataset = load_test_dataset()
    print(f"Loaded {len(test_dataset)} articles for evaluation")

    # Track processing time
    start_time = time.time()

    # Remove ground truth labels from articles for processing
    clean_articles = [{k: v for k, v in article.items()
                       if not k.startswith('ground_truth')}
                      for article in test_dataset]

    # Process articles through simplified workflow
    print("Processing articles through simplified workflow...")
    results = process_articles(clean_articles)

    # Add processed articles to KG
    for article in results:
        real_kg.add_article(article)

    processing_time = time.time() - start_time

    # Calculate metrics
    fact_accuracy = calculate_accuracy(results, test_dataset, aspect="fact_check")
    bias_precision, bias_recall = calculate_bias_precision_recall(results, test_dataset)

    # Calculate F1 score for bias detection
    f1_score = 2 * (bias_precision * bias_recall) / (bias_precision + bias_recall) if (
                                                                                              bias_precision + bias_recall) > 0 else 0

    # Save results to file
    os.makedirs('sys_evaluation/results', exist_ok=True)
    with open('sys_evaluation/results/news_workflow_results.json', 'w') as outfile:
        json.dump({
            'fact_accuracy': fact_accuracy,
            'bias_precision': bias_precision,
            'bias_recall': bias_recall,
            'bias_f1_score': f1_score,
            'avg_processing_time': processing_time / len(test_dataset),
            'total_articles': len(test_dataset),
            'evaluation_method': 'news_analysis_workflow'
        }, outfile, indent=2)

    # Print results
    print(f"\nNews Analysis Workflow Evaluation Results:")
    print(f"Fact-checking accuracy: {fact_accuracy:.2f}")
    print(f"Bias Detection Precision: {bias_precision:.2f}")
    print(f"Bias Detection Recall: {bias_recall:.2f}")
    print(f"Bias Detection F1 Score: {f1_score:.2f}")
    print(f"Average processing time per article: {processing_time / len(test_dataset):.2f} seconds")
    print(f"Total processing time: {processing_time:.2f} seconds")

    return results


def evaluate_direct_fact_checking():
    """Evaluation of direct fact checking route"""
    # Run diagnostic check
    print("Running AWS credential diagnostic test for fact checking route")
    diagnostic_check()

    # Create real knowledge graph and fact checker agent
    real_kg = KnowledgeGraph()
    fact_checker = FactCheckerAgent(kg=real_kg)

    # Load PolitiFact test data
    test_claims = load_politifact_dataset()
    print(f"Loaded {len(test_claims)} claims for fact checking evaluation")

    # Track processing time
    start_time = time.time()

    # Process each claim
    results = []
    for claim in test_claims:
        print(f"Processing claim: {claim['statement'][:50]}...")
        # Add graph_state for the agent
        graph_state = GraphState(news_query=claim['statement'])

        # Run fact checking
        result_state = fact_checker.run(graph_state)

        # Store result
        results.append({
            "statement": claim['statement'],
            "ground_truth_verdict": claim['ground_truth_verdict'],
            "system_verdict": result_state.fact_check_result
        })

    processing_time = time.time() - start_time

    # Calculate metrics
    correct = 0
    total = len(results)

    for result in results:
        system_verdict = result['system_verdict']['overall_verdict'].lower() if result['system_verdict'] else "unknown"
        ground_truth = result['ground_truth_verdict'].lower()

        # Map verdicts to boolean (true/false) for simpler comparison
        system_is_true = system_verdict in ['true', 'mostly-true', 'half-true']
        ground_truth_is_true = ground_truth in ['true', 'mostly-true', 'half-true']

        if system_is_true == ground_truth_is_true:
            correct += 1

    accuracy = correct / total if total > 0 else 0

    # Save results
    os.makedirs('sys_evaluation/results', exist_ok=True)
    with open('sys_evaluation/results/fact_checking_results.json', 'w') as outfile:
        json.dump({
            'accuracy': accuracy,
            'avg_processing_time': processing_time / total,
            'total_claims': total,
            'evaluation_method': 'direct_fact_checking'
        }, outfile, indent=2)

    # Print results
    print(f"\nDirect Fact Checking Evaluation Results:")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Average processing time per claim: {processing_time / total:.2f} seconds")
    print(f"Total processing time: {processing_time:.2f} seconds")

    return results


def combined_evaluation():
    """Run both evaluation paths and combine results"""
    # Set evaluation mode for the entire process
    os.environ["EVALUATION_MODE"] = "true"

    try:
        # Evaluate news analysis workflow
        print("=== Starting News Analysis Workflow Evaluation ===")
        news_results = evaluate_news_analysis_workflow()

        # Evaluate direct fact checking
        print("\n=== Starting Direct Fact Checking Evaluation ===")
        fact_check_results = evaluate_direct_fact_checking()

        # Combine results
        with open('sys_evaluation/results/news_workflow_results.json', 'r') as f1:
            news_metrics = json.load(f1)

        with open('sys_evaluation/results/fact_checking_results.json', 'r') as f2:
            fact_check_metrics = json.load(f2)

        combined_metrics = {
            'news_workflow': news_metrics,
            'fact_checking': fact_check_metrics,
            'overall_fact_accuracy': (news_metrics['fact_accuracy'] + fact_check_metrics['accuracy']) / 2
        }

        with open('sys_evaluation/results/combined_results.json', 'w') as outfile:
            json.dump(combined_metrics, outfile, indent=2)

        # Generate visualization chart
        generate_evaluation_chart('sys_evaluation/results/combined_results.json')

        print("\n=== Evaluation Complete ===")
        print(f"Overall fact checking accuracy: {combined_metrics['overall_fact_accuracy']:.2f}")

    except Exception as e:
        print(f"Combined evaluation failed: {str(e)}")


if __name__ == "__main__":
    combined_evaluation()