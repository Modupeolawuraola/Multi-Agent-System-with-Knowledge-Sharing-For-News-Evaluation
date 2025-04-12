import time
import json
import sys
import os
import logging
from src_v2.utils.aws_helpers import diagnostic_check

# Adding the root directory to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from src_v2.memory.schema import GraphState
# Import real KG instead of mock
from src_v2.memory.knowledge_graph import KnowledgeGraph  # Assuming this is the correct import
from sys_evaluation.metrics_updated import (
    calculate_bias_metrics,
    calculate_fact_check_metrics
)
from sys_evaluation.visualization_updated import generate_evaluation_chart, plot_confusion_matrix
from src_v2.workflow.simplified_workflow import process_articles
from src_v2.utils.aws_helpers import get_bedrock_llm
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


def load_bias_dataset():
    """Loading pre-labeled test articles"""
    import pandas as pd
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
    DATASET_PATH = os.path.join(BASE_DIR, 'sys_evaluation', 'test_dataset', 'test_bias_4_01_to_4_05.csv')

    # Load from CSV file
    df = pd.read_csv(DATASET_PATH)
    df['bias'] = df['bias'].str.lower().str.strip()
    df['bias'] = df['bias'].replace({
        'lean left': 'left',
        'lean right': 'right'
    })


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
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
    DATASET_PATH = os.path.join(BASE_DIR, 'sys_evaluation', 'test_dataset', 'mbfc_fact_checks.csv')

    # Load from CSV file
    df = pd.read_csv(DATASET_PATH)


    test_claims = []
    for _, row in df.iterrows():
        claim = {
            "claim": row['claim'],
            "date": row['date'],
            "ground_truth_verdict": row['rating']  # true, false, pants-fire, etc.
        }
        test_claims.append(claim)
    return test_claims


def evaluate_bias_workflow():
    """Evaluation using the simplified workflow with actual components"""
    # Run diagnostic check
    print("Running AWS credential diagnostic test")
    diagnostic_check()

    # Create real knowledge graph
    real_kg = KnowledgeGraph()

    # ==========================================================================================
    # need to load bias agent
    # Does bias agent add labels to data set?
    # ==========================================================================================

    # Load test data
    test_dataset = load_bias_dataset()
    print(f"Loaded {len(test_dataset)} articles for evaluation")

    # Track processing time
    start_time = time.time()

    # Remove ground truth labels from articles for processing
    clean_articles = [{k: v for k, v in article.items()
                       if not k.startswith('ground_truth_bias')}
                      for article in test_dataset]

    # Process articles through simplified workflow
    print("Processing articles through simplified workflow...")
    results = process_articles(clean_articles)

    # Add processed articles to KG
    # for article in results:
    #     real_kg.add_article(article)

    processing_time = time.time() - start_time
    bias_stats = calculate_bias_metrics(results, test_dataset)

    # Save results
    os.makedirs('sys_evaluation/results', exist_ok=True)
    with open('sys_evaluation/results/bias_results.json', 'w') as outfile:
        json.dump({
            'bias_accuracy': bias_stats['accuracy'],
            'bias_precision': bias_stats['precision'],
            'bias_recall': bias_stats['recall'],
            'bias_f1_score': bias_stats['f1_score'],
            'avg_processing_time': processing_time / len(test_dataset),
            'total_articles': len(test_dataset),
            'evaluation_method': 'news_bias_workflow'
        }, outfile, indent=2)

    y_true = [a['ground_truth_bias'] for a in test_dataset]
    y_pred = [a.get('predicted_bias') for a in results]
    plot_confusion_matrix(y_true, y_pred, labels=sorted(set(y_true)),
                          title="Bias Detection Confusion Matrix",
                          filename="sys_evaluation/results/bias_confusion_matrix.png")

    # Print results
    print("\nBias Analysis Workflow Evaluation Results:")
    print(f"Bias Accuracy: {bias_stats['accuracy']:.2f}")
    print(f"Bias Precision: {bias_stats['precision']:.2f}")
    print(f"Bias Recall: {bias_stats['recall']:.2f}")
    print(f"Bias F1 Score: {bias_stats['f1_score']:.2f}")
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
    fact_checker = FactCheckerAgent(llm=get_bedrock_llm(),kg=real_kg)

    # Load PolitiFact test data
    test_claims = load_politifact_dataset()
    print(f"Loaded {len(test_claims)} claims for fact checking evaluation")

    # Track processing time
    start_time = time.time()

    # Process each claim
    results = []
    for claim in test_claims:
        print(f"Processing claim: {claim['claim'][:50]}...")
        # Add graph_state for the agent
        graph_state = GraphState(news_query=claim['claim'])

        # Run fact checking
        result_state = fact_checker.run(graph_state)

        # Store result
        results.append({
            "statement": claim['claim'],
            "ground_truth_verdict": claim['ground_truth_verdict'],
            "system_verdict": result_state.fact_check_result
        })

    processing_time = time.time() - start_time

    # Calculate metrics
    fact_stats = calculate_fact_check_metrics(results)


    # Save results
    os.makedirs('sys_evaluation/results', exist_ok=True)
    with open('sys_evaluation/results/fact_checking_results.json', 'w') as outfile:
        json.dump({
            'fact_accuracy': fact_stats['accuracy'],
            'fact_precision': fact_stats['precision'],
            'fact_recall': fact_stats['recall'],
            'fact_f1_score': fact_stats['f1_score'],
            'avg_processing_time': processing_time / len(test_claims),
            'total_claims': len(test_claims),
            'evaluation_method': 'direct_fact_checking'
        }, outfile, indent=2)

    y_true = [c['ground_truth_verdict'] for c in results]
    y_pred = [c['system_verdict'] for c in results]
    plot_confusion_matrix(y_true, y_pred, labels=sorted(set(y_true)),
                          title="Fact Checking Confusion Matrix",
                          filename="sys_evaluation/results/fact_checking_confusion_matrix.png")

    # Print results
    print("\nDirect Fact Checking Evaluation Results:")
    print(f"Fact Accuracy: {fact_stats['accuracy']:.2f}")
    print(f"Fact Precision: {fact_stats['precision']:.2f}")
    print(f"Fact Recall: {fact_stats['recall']:.2f}")
    print(f"Fact F1 Score: {fact_stats['f1_score']:.2f}")
    print(f"Average processing time per claim: {processing_time / len(test_claims):.2f} seconds")
    print(f"Total processing time: {processing_time:.2f} seconds")

    return results

def combined_evaluation():
    """Run both evaluation paths and combine results"""
    # Set evaluation mode for the entire process
    os.environ["EVALUATION_MODE"] = "true"

    try:
        # Evaluate news analysis workflow
        print("=== Starting News Analysis Workflow Evaluation ===")
        evaluate_bias_workflow()

        # Evaluate direct fact checking
        print("\n=== Starting Direct Fact Checking Evaluation ===")
        evaluate_direct_fact_checking()

        # Combine results
        with open('sys_evaluation/results/bias_results.json', 'r') as f1:
            bias_metrics = json.load(f1)

        with open('sys_evaluation/results/fact_checking_results.json', 'r') as f2:
            fact_check_metrics = json.load(f2)

        combined_metrics = {
            'bias_workflow': bias_metrics,
            'fact_checking': fact_check_metrics,
            # 'overall_fact_accuracy': (news_metrics['fact_accuracy'] + fact_check_metrics['accuracy']) / 2
        }

        with open('sys_evaluation/results/combined_results.json', 'w') as outfile:
            json.dump(combined_metrics, outfile, indent=2)

        # Generate visualization chart
        generate_evaluation_chart('sys_evaluation/results/combined_results.json')

        # print("\n=== Evaluation Complete ===")
        # print(f"Overall fact checking accuracy: {combined_metrics['overall_fact_accuracy']:.2f}")

    except Exception as e:
        print(f"Combined evaluation failed: {str(e)}")


if __name__ == "__main__":
    # evaluate_bias_workflow()
    combined_evaluation()