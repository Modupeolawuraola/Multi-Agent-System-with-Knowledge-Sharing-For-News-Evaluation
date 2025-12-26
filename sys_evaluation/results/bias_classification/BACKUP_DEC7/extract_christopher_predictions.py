"""
Extract Christopher's predictions for the same 45 test articles
"""
import pandas as pd
from sklearn.metrics import accuracy_score
import numpy as np

print("="*60)
print("EXTRACTING CHRISTOPHER'S PREDICTIONS FOR TEST SET")
print("="*60)

# 1. Load the original dataset
bias_data = pd.read_csv('sys_evaluation/test_dataset/bias_cleaned_file.csv')
print(f"\nTotal articles in dataset: {len(bias_data)}")

# 2. Your split (same as evaluate_rag.py)
split_idx = int(len(bias_data) * 0.8)
print(f"Split point: {split_idx}")
print(f"Test articles: rows {split_idx} to {len(bias_data)-1}")
print(f"Number of test articles: {len(bias_data) - split_idx}")

# 3. Load Christopher's full results
christopher_results = pd.read_csv('sys_evaluation/results/bias_classification/bias_benchmark_comparison.csv')
print(f"\nChristopher's results: {len(christopher_results)} articles")

# 4. Extract only the test articles (rows split_idx onwards)
test_results = christopher_results.iloc[split_idx:].copy()
print(f"Extracted test results: {len(test_results)} articles")

# 5. Load your RAG results
rag_results = pd.read_csv('sys_evaluation/results/rag__bias_confusion.csv')
print(f"Your RAG results: {len(rag_results)} articles")

# 6. Verify they match
if len(rag_results) != len(test_results):
    print(f"\n⚠️  WARNING: Length mismatch!")
    print(f"RAG: {len(rag_results)}, Christopher's test set: {len(test_results)}")
else:
    print("\n✅ Lengths match!")

# 7. Create comparison dataframes
# Normalize case (left/Left -> left)
test_results['true_bias_lower'] = test_results['true_bias'].str.lower()
test_results['llm_only_lower'] = test_results['llm_only_prediction'].str.lower()
test_results['llm_kg_lower'] = test_results['llm_kg_prediction'].str.lower()

rag_results['true_bias_lower'] = rag_results['true_bias'].str.lower()
rag_results['predicted_lower'] = rag_results['predicted_bias'].str.lower()

# Verify ground truth matches
print("\nVerifying ground truth alignment...")
ground_truth_match = all(rag_results['true_bias_lower'].values == test_results['true_bias_lower'].values)

if ground_truth_match:
    print("✅ Ground truth matches perfectly!")
else:
    print("❌ Ground truth MISMATCH - articles may be in different order!")
    print("\nFirst 5 ground truths:")
    print("RAG:", rag_results['true_bias_lower'].head().tolist())
    print("Christopher:", test_results['true_bias_lower'].head().tolist())

# 8. Create comparison files for statistical testing
comparison_rag_llm_only = pd.DataFrame({
    'ground_truth': test_results['true_bias_lower'].values,
    'rag_prediction': rag_results['predicted_lower'].values,
    'llm_only_prediction': test_results['llm_only_lower'].values
})

comparison_rag_llm_kg = pd.DataFrame({
    'ground_truth': test_results['true_bias_lower'].values,
    'rag_prediction': rag_results['predicted_lower'].values,
    'llm_kg_prediction': test_results['llm_kg_lower'].values
})

comparison_llm_only_kg = pd.DataFrame({
    'ground_truth': test_results['true_bias_lower'].values,
    'llm_only_prediction': test_results['llm_only_lower'].values,
    'llm_kg_prediction': test_results['llm_kg_lower'].values
})

# 9. Save comparison files
comparison_rag_llm_only.to_csv('sys_evaluation/results/comparison_rag_vs_llm_only_bias.csv', index=False)
comparison_rag_llm_kg.to_csv('sys_evaluation/results/comparison_rag_vs_llm_kg_bias.csv', index=False)
comparison_llm_only_kg.to_csv('sys_evaluation/results/comparison_llm_only_vs_kg_bias.csv', index=False)

print("\n" + "="*60)
print("✅ SAVED COMPARISON FILES")
print("="*60)
print("  1. comparison_rag_vs_llm_only_bias.csv")
print("  2. comparison_rag_vs_llm_kg_bias.csv")
print("  3. comparison_llm_only_vs_kg_bias.csv")

# 10. Preview comparisons
print("\n" + "="*60)
print("PREVIEW: RAG vs LLM-only (first 10)")
print("="*60)
print(comparison_rag_llm_only.head(10).to_string())

print("\n" + "="*60)
print("PREVIEW: RAG vs LLM+KG (first 10)")
print("="*60)
print(comparison_rag_llm_kg.head(10).to_string())

print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)


print("\nAccuracy scores:")
# RAG accuracy
rag_mask = ~comparison_rag_llm_only['rag_prediction'].isna()
rag_acc = accuracy_score(
    comparison_rag_llm_only.loc[rag_mask, 'ground_truth'],
    comparison_rag_llm_only.loc[rag_mask, 'rag_prediction']
)

# LLM-only accuracy
llm_only_mask = ~comparison_llm_only_kg['llm_only_prediction'].isna()
llm_only_acc = accuracy_score(
    comparison_llm_only_kg.loc[llm_only_mask, 'ground_truth'],
    comparison_llm_only_kg.loc[llm_only_mask, 'llm_only_prediction']
)

# LLM+KG accuracy
llm_kg_mask = ~comparison_llm_only_kg['llm_kg_prediction'].isna()
llm_kg_acc = accuracy_score(
    comparison_llm_only_kg.loc[llm_kg_mask, 'ground_truth'],
    comparison_llm_only_kg.loc[llm_kg_mask, 'llm_kg_prediction']
)

print(f"  RAG:       {rag_acc:.3f}")
print(f"  LLM-only:  {llm_only_acc:.3f}")
print(f"  LLM+KG:    {llm_kg_acc:.3f}")