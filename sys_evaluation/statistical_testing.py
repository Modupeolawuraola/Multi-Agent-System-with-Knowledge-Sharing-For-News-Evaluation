"""
Statistical significance testing for baseline comparison
Adding confidence intervals and McNemar's test
"""
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, balanced_accuracy_score, cohen_kappa_score

def calculate_confidence_interval(y_true, y_pred, metric_func, n_iterations=1000):
    """Bootstrap confidence intervals for any metrics
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        metric_func: Metric function(y_true, y_pred) -> float
        n_iterations: Number of bootstrap samples
    Returns:
        dict with 'mean', 'lower', 'upper', 'std'
    """
    n = len(y_true)
    scores = []

    for _ in range(n_iterations):
        indices = np.random.choice(n, size=n, replace=True)
        y_true_boot = [y_true[i] for i in indices]  # FIXED: removed [indices]
        y_pred_boot = [y_pred[i] for i in indices]  # FIXED: removed [indices]

        try:
            score = metric_func(y_true_boot, y_pred_boot)  # FIXED: y_pred_boot not y_pred
            scores.append(score)
        except:
            continue

    scores = np.array(scores)
    return {
        'mean': np.mean(scores),
        'std': np.std(scores),
        'lower': np.percentile(scores, 2.5),
        'upper': np.percentile(scores, 97.5)
    }

def mcnemar_test(y_true, y_pred1, y_pred2):
    """
    McNemar's test for comparing two classifiers

    Returns:
        dict with 'statistic', 'p_value', 'significant'
    """
    from scipy.stats import chi2  # FIXED: use scipy instead of statsmodels

    # Create contingency table
    n00 = n01 = n10 = n11 = 0
    for true, pred1, pred2 in zip(y_true, y_pred1, y_pred2):
        correct1 = (pred1 == true)
        correct2 = (pred2 == true)

        if correct1 and correct2:
            n00 += 1
        elif not correct1 and not correct2:
            n11 += 1  # FIXED: both wrong
        elif correct1 and not correct2:
            n10 += 1  # FIXED: method1 correct, method2 wrong
        else:  # not correct1 and correct2
            n01 += 1  # FIXED: method1 wrong, method2 correct

    # McNemar's test statistic with continuity correction
    if (n01 + n10) == 0:
        statistic = 0
        p_value = 1.0
    else:
        statistic = ((abs(n01 - n10) - 1) ** 2) / (n01 + n10)
        p_value = 1 - chi2.cdf(statistic, df=1)

    return {
        'statistic': statistic,
        'p_value': p_value,  # FIXED: was 'p-value'
        'significant': p_value < 0.05,  # FIXED: was 0.5
        'n00': n00,
        'n01': n01,
        'n10': n10,
        'n11': n11
    }

def add_statistical_significance(y_true, y_pred1, y_pred2,
                                method1_name="RAG",
                                method2_name="LLM+KG"):
    """Calculate statistical significance test between two methods
    Args:
        y_true: Ground truth labels
        y_pred1: Predictions from method 1
        y_pred2: Predictions from method 2
        method1_name: Name of method 1
        method2_name: Name of method 2
    Returns:
        dict with confidence intervals and significance tests
    """
    print(f"\n== STATISTICAL SIGNIFICANCE TESTING ==")
    print(f"Comparing {method1_name} vs {method2_name}\n")

    # Confidence intervals for weighted F1
    f1_weighted = lambda y_true, y_pred: f1_score(y_true, y_pred, average='weighted', zero_division=0)

    ci1 = calculate_confidence_interval(y_true, y_pred1, f1_weighted)
    ci2 = calculate_confidence_interval(y_true, y_pred2, f1_weighted)

    print(f"{method1_name} Weighted F1: {ci1['mean']:.3f} "
          f"(95% CI: [{ci1['lower']:.3f}, {ci1['upper']:.3f}])")

    print(f"{method2_name} Weighted F1: {ci2['mean']:.3f} "
          f"(95% CI: [{ci2['lower']:.3f}, {ci2['upper']:.3f}])")

    # McNemar's test
    mcnemar_result = mcnemar_test(y_true, y_pred1, y_pred2)

    print(f"\nMcNemar's Test:")
    print(f"  Chi-square statistic: {mcnemar_result['statistic']:.4f}")
    print(f"  p-value: {mcnemar_result['p_value']:.4f}")
    print(f"  Significant at α=0.05: {mcnemar_result['significant']}")

    if mcnemar_result['significant']:
        if ci2['mean'] > ci1['mean']:
            print(f"✓ {method2_name} is statistically significantly BETTER than {method1_name}.")
        else:
            print(f"✓ {method1_name} is statistically significantly BETTER than {method2_name}.")
    else:
        print(f"✗ No statistically significant difference.")

    return {
        'method1_ci': ci1,
        'method2_ci': ci2,
        'mcnemar_result': mcnemar_result
    }


if __name__ == "__main__":
    print("Statistical Testing Module - Ready to use!")

