import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import os


def generate_evaluation_chart(result_file='sys_evaluation/results/evaluation_results.json'):
    """Generate chart from the evaluation result"""
    # Load result
    if not os.path.exists(result_file):
        print(f"Result file not found: {result_file}")
        return

    with open(result_file, 'r') as f:
        result = json.load(f)

    # Creating an output directory
    os.makedirs('sys_evaluation/results/charts', exist_ok=True)

    # Chart 1- creating accuracy metrics chart
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

    print("Chart saved to sys_evaluation/results/charts/")


if __name__ == '__main__':
    generate_evaluation_chart()