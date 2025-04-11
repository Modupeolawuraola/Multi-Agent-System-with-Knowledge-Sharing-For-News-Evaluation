import matplotlib.pyplot as plt
import json
import os


def generate_evaluation_chart(result_file='sys_evaluation/results/combined_results.json'):
    """Generate charts for both bias and fact-checking metrics, separately."""
    if not os.path.exists(result_file):
        print(f"Result file not found: {result_file}")
        return

    with open(result_file, 'r') as f:
        result = json.load(f)

    # Create output directory for charts
    os.makedirs('sys_evaluation/results/charts', exist_ok=True)

    # 1) Chart for News Workflow (Bias) metrics, if present
    if 'news_workflow' in result:
        news_data = result['news_workflow']

        # We'll look for standard bias metrics
        bias_metrics = ['bias_accuracy', 'bias_precision', 'bias_recall', 'bias_f1_score']
        # Filter for keys that exist to avoid KeyErrors
        found_bias_metrics = [(m, news_data[m]) for m in bias_metrics if m in news_data]

        if found_bias_metrics:
            plt.figure(figsize=(6, 4))
            metric_labels = [m[0] for m in found_bias_metrics]
            metric_values = [m[1] for m in found_bias_metrics]

            plt.bar(metric_labels, metric_values)
            plt.ylim(0, 1.0)  # these metrics are typically in [0, 1]
            plt.title('News Workflow Bias Metrics')
            plt.ylabel('Score (0-1)')
            plt.grid(axis='y', linestyle='--', alpha=0.5)

            # Place numeric labels above each bar
            for i, v in enumerate(metric_values):
                plt.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom')

            plt.tight_layout()
            plt.savefig('sys_evaluation/results/charts/news_workflow_bias_metrics.png')
            plt.close()
        else:
            print("No bias metrics found in 'news_workflow' section.")

    # 2) Chart for Direct Fact Checking metrics, if present
    if 'fact_checking' in result:
        fact_data = result['fact_checking']

        # We'll look for standard fact metrics
        fact_metrics = ['fact_accuracy', 'fact_precision', 'fact_recall', 'fact_f1_score']
        found_fact_metrics = [(m, fact_data[m]) for m in fact_metrics if m in fact_data]

        if found_fact_metrics:
            plt.figure(figsize=(6, 4))
            metric_labels = [m[0] for m in found_fact_metrics]
            metric_values = [m[1] for m in found_fact_metrics]

            plt.bar(metric_labels, metric_values)
            plt.ylim(0, 1.0)
            plt.title('Direct Fact Checking Metrics')
            plt.ylabel('Score (0-1)')
            plt.grid(axis='y', linestyle='--', alpha=0.5)

            for i, v in enumerate(metric_values):
                plt.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom')

            plt.tight_layout()
            plt.savefig('sys_evaluation/results/charts/fact_checking_metrics.png')
            plt.close()
        else:
            print("No fact-check metrics found in 'fact_checking' section.")

    # 3) Chart for overall or combined metrics (e.g., overall_fact_accuracy), if present
    if 'overall_fact_accuracy' in result:
        plt.figure(figsize=(5, 4))
        val = result['overall_fact_accuracy']
        plt.bar(['Overall Fact Accuracy'], [val])
        plt.ylim(0, 1.0)
        plt.title('Overall Fact Checking Accuracy')
        plt.grid(axis='y', linestyle='--', alpha=0.5)
        plt.text(0, val + 0.02, f'{val:.2f}', ha='center', va='bottom')
        plt.tight_layout()
        plt.savefig('sys_evaluation/results/charts/overall_fact_accuracy.png')
        plt.close()

    # If we do NOT find 'news_workflow' or 'fact_checking', treat the file as a
    # single-workflow result (old behavior):
    if 'news_workflow' not in result and 'fact_checking' not in result:
        plt.figure(figsize=(6, 4))
        # Attempt to find these keys in the top-level dictionary:
        # fact_accuracy, bias_precision, bias_recall, bias_f1_score ...
        single_metrics = ['fact_accuracy', 'bias_accuracy', 'bias_precision', 'bias_recall', 'bias_f1_score']
        single_values = [(m, result[m]) for m in single_metrics if m in result]

        if single_values:
            labels = [m[0] for m in single_values]
            vals = [m[1] for m in single_values]

            plt.bar(labels, vals)
            plt.ylim(0, 1.0)
            plt.title('Single Workflow Evaluation Metrics')
            plt.ylabel('Score (0-1)')
            plt.grid(axis='y', linestyle='--', alpha=0.5)

            for i, v in enumerate(vals):
                plt.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom')

            plt.tight_layout()
            plt.savefig('sys_evaluation/results/charts/single_workflow_metrics.png')
            plt.close()
        else:
            print("No recognized metrics found in this result file.")

    print("Charts saved to sys_evaluation/results/charts/")
    return 'sys_evaluation/results/charts/'
