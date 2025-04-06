import matplotlib.pyplot as plt
import json
import os


def generate_evaluation_chart(result_file='sys_evaluation/results/combined_results.json'):
    """Generate chart from the combined evaluation results"""
    # Load result
    if not os.path.exists(result_file):
        print(f"Result file not found: {result_file}")
        return

    with open(result_file, 'r') as f:
        result = json.load(f)

    # Creating an output directory
    os.makedirs('sys_evaluation/results/charts', exist_ok=True)

    # Check if we have combined results or single workflow results
    if 'news_workflow' in result and 'fact_checking' in result:
        # We have combined results

        # Chart 1: News workflow metrics
        plt.figure(figsize=(10, 6))
        news_metrics = ['fact_accuracy', 'bias_precision', 'bias_recall', 'bias_f1_score']
        news_values = [result['news_workflow'].get(metric, 0) for metric in news_metrics]

        plt.bar(news_metrics, news_values, color=['blue', 'green', 'orange', 'yellow'])
        plt.ylim(0, 1.0)
        plt.title('News Analysis Workflow Metrics')
        plt.ylabel('Score (0-1)')
        plt.grid(axis='y', linestyle='--', alpha=0.5)

        # Add values on top of bars
        for i, v in enumerate(news_values):
            plt.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig('sys_evaluation/results/charts/news_workflow_metrics.png')

        # Chart 2: Direct fact checking
        plt.figure(figsize=(8, 5))
        plt.bar(['Fact Checking Accuracy'], [result['fact_checking']['accuracy']], color='red')
        plt.ylim(0, 1.0)
        plt.title('Direct Fact Checking Accuracy')
        plt.ylabel('Accuracy Score (0-1)')
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.text(0, result['fact_checking']['accuracy'] + 0.02,
                 f"{result['fact_checking']['accuracy']:.2f}",
                 ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig('sys_evaluation/results/charts/fact_checking_accuracy.png')

        # Chart 3: Combined performance
        plt.figure(figsize=(10, 6))
        combined_metrics = [
            'News Workflow\nFact Accuracy',
            'Direct Fact\nChecking Accuracy',
            'Overall\nFact Accuracy',
            'News Workflow\nBias F1 Score'
        ]
        combined_values = [
            result['news_workflow']['fact_accuracy'],
            result['fact_checking']['accuracy'],
            result['overall_fact_accuracy'],
            result['news_workflow']['bias_f1_score']
        ]

        plt.bar(combined_metrics, combined_values, color=['blue', 'red', 'purple', 'green'])
        plt.ylim(0, 1.0)
        plt.title('Combined System Performance')
        plt.ylabel('Score (0-1)')
        plt.grid(axis='y', linestyle='--', alpha=0.5)

        # Add values on top of bars
        for i, v in enumerate(combined_values):
            plt.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig('sys_evaluation/results/charts/combined_performance.png')

    else:
        # Original single workflow visualization
        plt.figure(figsize=(10, 6))
        metrics = ['fact_accuracy', 'bias_precision', 'bias_recall', 'bias_f1_score']
        values = [result.get(metric, 0) for metric in metrics]

        plt.bar(metrics, values, color=['blue', 'green', 'orange', 'yellow'])
        plt.ylim(0, 1.0)
        plt.title('Evaluation Metrics')
        plt.ylabel('Accuracy Score (0-1)')
        plt.grid(axis='y', linestyle='--', alpha=0.5)

        # Add values on top of bars
        for i, v in enumerate(values):
            plt.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig('sys_evaluation/results/charts/accuracy_metrics.png')

    print("Charts saved to sys_evaluation/results/charts/")
    return 'sys_evaluation/results/charts/'