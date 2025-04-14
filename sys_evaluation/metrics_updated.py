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
    compute fact-check metrics, assuming your pipeline sets
    results[i]['system_verdict']['overall_verdict'] or similar.

    """

    # # Convert system verdict to 'true'/'false' or something binary
    # def system_label(verdict_str):
    #     verdict_str = verdict_str.lower()
    #     if verdict_str in ['true', 'mostly-true', 'half-true']:
    #         return "true"
    #     return "false"
    #
    # # Convert ground truth to 'true'/'false' or something binary
    # def ground_label(gt_verdict_str):
    #     gt_verdict_str = gt_verdict_str.lower()
    #     if gt_verdict_str in ['true', 'mostly-true']:
    #         return "true"
    #     return "false"

    y_pred = []
    y_true = []

    for r in results:
        system_verdict_dict = r['system_verdict'] or {}
        verdict_str = system_verdict_dict.get('overall_verdict', 'unknown').lower()
        gt_str = r['ground_truth_verdict'].lower()

        y_pred.append(verdict_str)
        y_true.append(gt_str)

    TP, FP, TN, FN = calculate_confusion_matrix(y_pred, y_true, positive_label="true")
    metrics = calculate_metrics_from_confusion_matrix(y_true, y_pred, positive_label="true")

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    metrics["macro_f1"] = report["macro avg"]["f1-score"]
    metrics["weighted_f1"] = report["weighted avg"]["f1-score"]
    metrics["confusion_matrix"] = confusion_matrix(y_true, y_pred, labels=["true", "false"]).tolist()

    return calculate_metrics_from_confusion_matrix(TP, FP, TN, FN)
