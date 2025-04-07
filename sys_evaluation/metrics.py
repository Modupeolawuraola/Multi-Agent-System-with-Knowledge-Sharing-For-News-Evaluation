def calculate_accuracy(results, test_dataset, aspect="fact_check"):
    """Calculate the accuracy of fact-checking

    Args:
        results: List of processed articles with fact_check data
        test_dataset: List of original articles with ground truth labels
        aspect: Which aspect to evaluate ('fact_check' or 'bias')

    Returns:
        Accuracy score from 0.0 to 1.0
    """
    correct = 0
    total = 0

    for i, article in enumerate(results):
        if aspect == "fact_check":
            # Compare each verified claim to ground truth
            for claim in article.get('fact_check', {}).get('verified_claims', []):
                for gt_claim in test_dataset[i]['ground_truth_facts']:
                    if claim['claim'] == gt_claim['claim']:
                        # Check if verification matches ground truth
                        if claim['verification']['is_verified'] == gt_claim['is_true']:
                            correct += 1
                        total += 1

    return correct / total if total > 0 else 0.0


def calculate_bias_precision_recall(results, test_dataset):
    """Calculate precision and recall for bias detection

    Args:
        results: List of processed articles with bias_analysis data
        test_dataset: List of original articles with ground truth bias labels

    Returns:
        Tuple of (precision, recall)
    """
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    for i, article in enumerate(results):
        # Get system's bias assessment
        # Updated to check confidence_score over 50 or based on overall_assessment
        system_bias_analysis = article.get('bias_analysis', {})
        system_has_bias = False

        # Check different ways bias might be indicated in your system
        if 'confidence_score' in system_bias_analysis:
            system_has_bias = system_bias_analysis.get('confidence_score', 0) > 50
        elif 'overall_assessment' in system_bias_analysis:
            biased_terms = ['biased', 'bias', 'partial', 'slanted', 'skewed']
            assessment = system_bias_analysis.get('overall_assessment', '').lower()
            system_has_bias = any(term in assessment for term in biased_terms)
        elif 'has_bias' in system_bias_analysis:
            system_has_bias = system_bias_analysis.get('has_bias', False)

        # Get ground truth - consider any non-neutral or non-factual label as biased
        truth_label = test_dataset[i]['ground_truth_bias'].lower()
        truth_has_bias = truth_label not in ['neutral', 'factual', 'unbiased']

        if system_has_bias and truth_has_bias:
            true_positives += 1
        elif system_has_bias and not truth_has_bias:
            false_positives += 1
        elif not system_has_bias and truth_has_bias:
            false_negatives += 1

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0

    return precision, recall