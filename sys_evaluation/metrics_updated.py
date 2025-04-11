import math

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


def calculate_metrics_from_confusion_matrix(TP, FP, TN, FN):
    """
    Given confusion matrix terms, compute accuracy, precision, recall, f1.
    Returns a dictionary of these metrics.
    """
    accuracy = (TP + TN) / float(TP + TN + FP + FN) if (TP + TN + FP + FN) else 0.0
    precision = TP / float(TP + FP) if (TP + FP) else 0.0
    recall = TP / float(TP + FN) if (TP + FN) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }


def calculate_bias_metrics(results, ground_truth):
    """
    Example of how to compute bias metrics, assuming your pipeline sets
    results[i]['predicted_bias'] for each article.
    :param results: The system output for each article (must contain "predicted_bias").
    :param ground_truth: The ground truth data (must contain "ground_truth_bias").
    """
    y_pred = [res.get('predicted_bias', 'unknown') for res in results]
    y_true = [gt['ground_truth_bias'] for gt in ground_truth]

    # If you consider 'biased' vs. 'unbiased' as binary classification,
    # pick which label is "positive_label" to measure precision/recall.
    positive_label = "biased"  # or "left", "right", etc. as your use-case demands

    TP, FP, TN, FN = calculate_confusion_matrix(y_pred, y_true, positive_label)
    return calculate_metrics_from_confusion_matrix(TP, FP, TN, FN)


def calculate_fact_check_metrics(results):
    """
    Example of how to compute fact-check metrics, assuming your pipeline sets
    results[i]['system_verdict']['overall_verdict'] or similar.
    'true' group: ['true','mostly-true','half-true']
    'false' group: everything else
    """

    # Convert system verdict to 'true'/'false' or something binary
    def system_label(verdict_str):
        verdict_str = verdict_str.lower()
        if verdict_str in ['true', 'mostly-true', 'half-true']:
            return "true"
        return "false"

    # Convert ground truth to 'true'/'false' or something binary
    def ground_label(gt_verdict_str):
        gt_verdict_str = gt_verdict_str.lower()
        if gt_verdict_str in ['true', 'mostly-true', 'half-true']:
            return "true"
        return "false"

    y_pred = []
    y_true = []
    for r in results:
        # system_verdict might be None if no result
        system_verdict_dict = r['system_verdict'] or {}
        verdict_str = system_verdict_dict.get('overall_verdict', 'unknown')
        y_pred.append(system_label(verdict_str))

        gt_str = r['ground_truth_verdict']
        y_true.append(ground_label(gt_str))

    positive_label = "true"
    TP, FP, TN, FN = calculate_confusion_matrix(y_pred, y_true, positive_label)
    return calculate_metrics_from_confusion_matrix(TP, FP, TN, FN)
