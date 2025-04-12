import matplotlib.pyplot as plt
import json
import os
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


def plot_metrics(metrics: dict, title: str, filename: str):
    """Helper function to plot and save metric bar charts."""
    labels = list(metrics.keys())
    values = list(metrics.values())

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values)
    plt.ylim(0, 1.0)
    plt.title(title)
    plt.ylabel('Score (0-1)')
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    for i, v in enumerate(values):
        plt.text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def generate_evaluation_chart(result_file='sys_evaluation/results/combined_results.json'):
    """Generate charts for both bias and fact-checking metrics, separately."""
    chart_paths = []
    if not os.path.exists(result_file):
        print(f"Result file not found: {result_file}")
        return

    with open(result_file, 'r') as f:
        result = json.load(f)

    # Create output directory for charts
    chart_dir = 'sys_evaluation/results/charts'
    os.makedirs('chart_dir', exist_ok=True)

    def get_metrics(data, keys):
        return {k: data[k] for k in keys if k in data}

    # 1) Chart for News Workflow (Bias) metrics, if present
    if 'bias_workflow' in result:
        bias_data = result['news_workflow']

        bias_keys = ['bias_accuracy', 'bias_precision', 'bias_recall', 'bias_f1_score']
        bias_metrics = get_metrics(result['news_workflow'], bias_keys)

        if bias_metrics:
            chart_path = os.path.join(chart_dir, 'bias_metrics.png')
            plot_metrics(bias_metrics, 'Bias Metrics', chart_path)
            chart_paths.append(chart_path)
        else:
            print("⚠️ No bias metrics found in 'news_workflow' section.")

    # 2) Chart for Direct Fact Checking metrics, if present
    if 'fact_checking' in result:
        fact_data = result['fact_checking']

        # We'll look for standard fact metrics
        fact_keys = ['fact_accuracy', 'fact_precision', 'fact_recall', 'fact_f1_score']
        fact_metrics = get_metrics(result['fact_checking'], fact_keys)

        if fact_metrics:
            chart_path = os.path.join(chart_dir, 'fact_checking_metrics.png')
            plot_metrics(fact_metrics, 'Direct Fact Checking Metrics', chart_path)
            chart_paths.append(chart_path)
        else:
            print("⚠️ No fact-check metrics found in 'fact_checking' section.")

    print("Charts saved to sys_evaluation/results/charts/")
    return 'sys_evaluation/results/charts/'


def plot_confusion_matrix(y_true, y_pred, labels, title, filename):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap=plt.cm.Blues)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
