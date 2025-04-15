import math
from sklearn.metrics import (
    classification_report, balanced_accuracy_score,
    cohen_kappa_score, matthews_corrcoef, confusion_matrix
)

def calculate_confusion_matrix(y_pred, y_true, positive_label):
    """
    Given predicted labels and ground truth labels, and a 'positive' label,
    compute confusion matrix terms: TP, FP, TN, FN.

    """
    TP = FP = TN = FN = 0
    for pred, true in zip(y_pred, y_true):
        pred_is_pos = (pred == positive_label)
        true_is_pos = (true == positive_label)

        if pred_is_pos and true_is_pos:
            TP += 1
        elif pred_is_pos and not true_is_pos:
            FP += 1
        elif not pred_is_pos and not true_is_pos:
            TN += 1
        elif not pred_is_pos and true_is_pos:
            FN += 1

    return TP, FP, TN, FN


def calculate_metrics_from_confusion_matrix(y_true, y_pred, positive_label):
    """
    Given confusion matrix terms, compute accuracy, precision, recall, f1.
    Returns a dictionary of these metrics.
    """
    TP, FP, TN, FN = calculate_confusion_matrix(y_true, y_pred, positive_label)
    accuracy = (TP + TN) / float(TP + TN + FP + FN) if (TP + TN + FP + FN) else 0.0
    precision = TP / float(TP + FP) if (TP + FP) else 0.0
    recall = TP / float(TP + FN) if (TP + FN) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    kappa = cohen_kappa_score(y_true, y_pred)
    mcc = matthews_corrcoef(y_true, y_pred)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "cohen_kappa": kappa,
        "mcc": mcc
    }


def calculate_bias_metrics(y_true, y_pred, label_order=None):

    if label_order is None:
        label_order = ['left', 'center','right']

    report = classification_report(
        y_true,
        y_pred,
        labels=label_order,
        output_dict=True,
        zero_division=0
    )
    macro_f1 = report['macro avg']['f1-score']
    weighted_f1 = report['weighted avg']['f1-score']
    kappa = cohen_kappa_score(y_true, y_pred)
    mcc = matthews_corrcoef(y_true, y_pred)
    balanced_acc = balanced_accuracy_score(y_true, y_pred)

    return {
        "classification_report": report,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "cohen_kappa": kappa,
        "mcc": mcc,
        "balanced_accuracy": balanced_acc
    }


def calculate_fact_check_metrics(results):
    """
    Compute fact-check evaluation metrics from system results.
    Each result must contain:
    - system_verdict['overall_verdict'] -> prediction (string)
    - ground_truth_verdict -> actual label (string)
    """
    y_true = []
    y_pred = []

    for r in results:
        pred_raw = (r.get("system_verdict") or {}).get("overall_verdict", "unknown")
        true_raw = r.get("ground_truth_verdict", "unknown")
        y_pred.append(pred_raw.strip().lower())
        y_true.append(true_raw.strip().lower())

    # Main report
    report = classification_report(
        y_true, y_pred,
        labels=["true", "false"],
        output_dict=True,
        zero_division=0
    )

    metrics = {
        "classification_report": report,
        "accuracy": report.get("accuracy", 0.0),
        "macro_f1": report.get("macro avg", {}).get("f1-score", 0.0),
        "weighted_f1": report.get("weighted avg", {}).get("f1-score", 0.0),
        "cohen_kappa": cohen_kappa_score(y_true, y_pred),
        "mcc": matthews_corrcoef(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=["true", "false"]).tolist()
    }

    return metrics
