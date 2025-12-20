"""
Calculate Per-Class Metrics for RAG Baseline
Extracts precision, recall, and F1 scores from confusion matrices
to update Tables 3 & 4 in the paper
"""

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from pathlib import Path
np.random.seed(42)

def calculate_metrics_from_confusion_matrix(y_true, y_pred, labels):
    """
    Calculate per-class and aggregate metrics

    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: List of class labels

    Returns:
        dict: Metrics for each class and aggregates
    """
    # Get classification report
    report = classification_report(y_true, y_pred, labels=labels,
                                   output_dict=True, zero_division=0)

    # Format results
    metrics = {}

    for label in labels:
        if label in report:
            metrics[label] = {
                'precision': report[label]['precision'],
                'recall': report[label]['recall'],
                'f1-score': report[label]['f1-score'],
                'support': report[label]['support']
            }

    # Add aggregate metrics
    for avg_type in ['weighted avg', 'macro avg']:
        if avg_type in report:
            metrics[avg_type] = {
                'precision': report[avg_type]['precision'],
                'recall': report[avg_type]['recall'],
                'f1-score': report[avg_type]['f1-score'],
                'support': report[avg_type]['support']
            }

    return metrics


def process_bias_results():
    """Process RAG bias detection results"""

    print("\n" + "=" * 60)
    print("BIAS DETECTION - RAG BASELINE METRICS")
    print("=" * 60)

    # Load RAG bias confusion results
    bias_path = Path('../results/bias_classification/rag__bias_confusion.csv')

    if not bias_path.exists():
        print(f"❌ Error: {bias_path} not found!")
        return None

    df = pd.read_csv(bias_path)

    # Extract predictions and ground truth
    # FIXED: Use correct column names
    y_true = df['true_bias'].values
    y_pred = df['predicted_bias'].values

    # FIXED: Handle "unknown" predictions - treat as wrong prediction
    # Replace "unknown" with "Center" (or any valid label) so sklearn doesn't break
    y_pred = np.array([pred if pred != 'unknown' else 'Center' for pred in y_pred])

    # FIXED: Standardize case (your data has lowercase, but we want title case)
    y_true = np.array([str(label).title() for label in y_true])
    y_pred = np.array([str(label).title() for label in y_pred])

    # Define class labels
    labels = ['Left', 'Center', 'Right']

    print(f"\n🔍 Debug: Found {len(y_true)} predictions")
    print(f"🔍 Debug: Unique true labels: {np.unique(y_true)}")
    print(f"🔍 Debug: Unique predicted labels: {np.unique(y_pred)}")

    # Calculate metrics
    metrics = calculate_metrics_from_confusion_matrix(y_true, y_pred, labels)

    # Print results in table format
    print("\n📊 RAG Baseline - Bias Detection Per-Class Metrics:\n")
    print(f"{'Class':<15} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}")
    print("-" * 60)

    for label in labels:
        if label in metrics:
            m = metrics[label]
            print(f"{label:<15} {m['precision']:>10.2f} {m['recall']:>10.2f} "
                  f"{m['f1-score']:>10.2f} {m['support']:>10.0f}")

    print("-" * 60)
    print(f"{'Macro Avg':<15} {metrics['macro avg']['precision']:>10.2f} "
          f"{metrics['macro avg']['recall']:>10.2f} "
          f"{metrics['macro avg']['f1-score']:>10.2f} "
          f"{metrics['macro avg']['support']:>10.0f}")

    print(f"{'Weighted Avg':<15} {metrics['weighted avg']['precision']:>10.2f} "
          f"{metrics['weighted avg']['recall']:>10.2f} "
          f"{metrics['weighted avg']['f1-score']:>10.2f} "
          f"{metrics['weighted avg']['support']:>10.0f}")

    # Generate LaTeX table code
    print("\n📝 LaTeX Code for Paper (Table 3 - Add RAG Column):\n")
    print("% RAG Baseline Column")
    for label in labels:
        if label in metrics:
            m = metrics[label]
            print(f"{m['precision']:.2f} & {m['recall']:.2f} & {m['f1-score']:.2f} \\\\")
    print(f"% Weighted Average")
    print(f"{metrics['weighted avg']['precision']:.2f} & "
          f"{metrics['weighted avg']['recall']:.2f} & "
          f"{metrics['weighted avg']['f1-score']:.2f} \\\\")

    return metrics


def process_factcheck_results():
    """Process RAG fact-checking results"""

    print("\n" + "=" * 60)
    print("FACT-CHECKING - RAG BASELINE METRICS")
    print("=" * 60)

    # Load RAG fact-checking confusion results
    factcheck_path = Path('../results/fact_checking/rag_factcheck_confusion_new_2.csv')

    if not factcheck_path.exists():
        print(f"❌ Error: {factcheck_path} not found!")
        return None

    df = pd.read_csv(factcheck_path)

    # Use correct column names
    y_true = df['true_bias'].apply(lambda x: str(x).lower() == 'true').values
    y_pred = df['predicted_bias'].apply(lambda x: str(x).lower() == 'true').values

    # FIXED: Use STRING labels instead of boolean to match sklearn behavior
    # Convert to strings for sklearn
    y_true_str = np.array(['True' if x else 'False' for x in y_true])
    y_pred_str = np.array(['True' if x else 'False' for x in y_pred])

    # Define class labels as STRINGS
    labels = ['True', 'False']

    print(f"\n🔍 Debug: Found {len(y_true)} predictions")
    print(f"🔍 Debug: Unique true labels: {np.unique(y_true_str)}")
    print(f"🔍 Debug: Unique predicted labels: {np.unique(y_pred_str)}")

    # Calculate metrics with string labels
    metrics = calculate_metrics_from_confusion_matrix(y_true_str, y_pred_str, labels)

    # Print results in table format
    print("\n📊 RAG Baseline - Fact-Checking Per-Class Metrics:\n")
    print(f"{'Class':<15} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}")
    print("-" * 60)

    # NOW THIS WILL WORK - labels match metrics keys
    for label in labels:
        if label in metrics:
            m = metrics[label]
            print(f"{label:<15} {m['precision']:>10.2f} {m['recall']:>10.2f} "
                  f"{m['f1-score']:>10.2f} {m['support']:>10.0f}")

    print("-" * 60)
    print(f"{'Macro Avg':<15} {metrics['macro avg']['precision']:>10.2f} "
          f"{metrics['macro avg']['recall']:>10.2f} "
          f"{metrics['macro avg']['f1-score']:>10.2f} "
          f"{metrics['macro avg']['support']:>10.0f}")

    print(f"{'Weighted Avg':<15} {metrics['weighted avg']['precision']:>10.2f} "
          f"{metrics['weighted avg']['recall']:>10.2f} "
          f"{metrics['weighted avg']['f1-score']:>10.2f} "
          f"{metrics['weighted avg']['support']:>10.0f}")

    # Generate LaTeX table code
    print("\n📝 LaTeX Code for Paper (Table 4 - Add RAG Column):\n")
    print("% RAG Baseline Column")
    for label in labels:
        if label in metrics:
            m = metrics[label]
            print(f"{m['precision']:.2f} & {m['recall']:.2f} & {m['f1-score']:.2f} \\\\")
    print(f"% Weighted Average")
    print(f"{metrics['weighted avg']['precision']:.2f} & "
          f"{metrics['weighted avg']['recall']:.2f} & "
          f"{metrics['weighted avg']['f1-score']:.2f} \\\\")

    return metrics


def save_metrics_summary(bias_metrics, factcheck_metrics):
    """Save metrics summary to file for reference"""

    output_path = Path('../results/rag_baseline_metrics_summary.txt')

    with open(output_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("RAG BASELINE - PER-CLASS METRICS SUMMARY\n")
        f.write("=" * 60 + "\n\n")

        # Bias metrics
        f.write("BIAS DETECTION:\n")
        f.write("-" * 60 + "\n")
        if bias_metrics:
            for label in ['Left', 'Center', 'Right']:
                if label in bias_metrics:
                    m = bias_metrics[label]
                    f.write(f"{label}: P={m['precision']:.3f}, "
                            f"R={m['recall']:.3f}, F1={m['f1-score']:.3f}\n")
            f.write(f"Weighted Avg: P={bias_metrics['weighted avg']['precision']:.3f}, "
                    f"R={bias_metrics['weighted avg']['recall']:.3f}, "
                    f"F1={bias_metrics['weighted avg']['f1-score']:.3f}\n")

        f.write("\n")

        # Fact-checking metrics
        f.write("FACT-CHECKING:\n")
        f.write("-" * 60 + "\n")
        if factcheck_metrics:
            for label, name in [(True, 'True'), (False, 'False')]:
                if label in factcheck_metrics:
                    m = factcheck_metrics[label]
                    f.write(f"{name}: P={m['precision']:.3f}, "
                            f"R={m['recall']:.3f}, F1={m['f1-score']:.3f}\n")
            f.write(f"Weighted Avg: P={factcheck_metrics['weighted avg']['precision']:.3f}, "
                    f"R={factcheck_metrics['weighted avg']['recall']:.3f}, "
                    f"F1={factcheck_metrics['weighted avg']['f1-score']:.3f}\n")

    print(f"\n✅ Metrics summary saved to: {output_path}")


def main():
    """Calculate and display RAG baseline metrics"""

    print("=" * 60)
    print("CALCULATING RAG BASELINE PER-CLASS METRICS")
    print("=" * 60)

    # Process both tasks
    bias_metrics = process_bias_results()
    factcheck_metrics = process_factcheck_results()

    # Save summary
    if bias_metrics or factcheck_metrics:
        save_metrics_summary(bias_metrics, factcheck_metrics)

    print("\n" + "=" * 60)
    print("✅ RAG METRICS CALCULATION COMPLETE!")
    print("=" * 60)
    print("\n💡 Next Steps:")
    print("  1. Copy the LaTeX code above into your paper")
    print("  2. Add RAG column to Table 3 (Bias Detection)")
    print("  3. Add RAG column to Table 4 (Fact-Checking)")
    print("  4. Update table captions to mention 3-way comparison")


if __name__ == "__main__":
    main()