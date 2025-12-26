"""
Extract fact-checking predictions - matching RAG's incomplete results
"""
import pandas as pd

print("=" * 60)
print("EXTRACTING FACT-CHECKING PREDICTIONS")
print("=" * 60)

# 1. Load test dataset to get claim order
print("\nLoading test dataset...")
test_data = pd.read_csv('test_dataset/fact_check_test.tsv', sep='\t')
print(f"Test dataset: {len(test_data)} claims")
print(f"Columns: {test_data.columns.tolist()}")

# 2. Load RAG results
print("\nLoading RAG results...")
rag_results = pd.read_csv('results/rag_factcheck_confusion.csv')
print(f"RAG results: {len(rag_results)} rows")

# Fix column names
rag_results.rename(columns={
    'true_bias': 'true_verdict',
    'predicted_bias': 'predicted_verdict'
}, inplace=True)"""
Extract fact-checking predictions - matching RAG's incomplete results
"""
import pandas as pd

print("=" * 60)
print("EXTRACTING FACT-CHECKING PREDICTIONS")
print("=" * 60)

# 1. Load test dataset to get claim order
print("\nLoading test dataset...")
test_data = pd.read_csv('test_dataset/fact_check_test.tsv', sep='\t')
print(f"Test dataset: {len(test_data)} claims")
print(f"Columns: {test_data.columns.tolist()}")

# 2. Load RAG results
print("\nLoading RAG results...")
rag_results = pd.read_csv('results/rag_factcheck_confusion.csv')
print(f"RAG results: {len(rag_results)} rows")

# Fix column names
rag_results.rename(columns={
    'true_bias': 'true_verdict',
    'predicted_bias': 'predicted_verdict'
}, inplace=True)

# Remove empty rows
rag_complete = rag_results[rag_results['true_verdict'].notna()].copy()
print(f"Complete RAG predictions: {len(rag_complete)}")

# 3. Load Christopher's results
print("\nLoading LLM-only results...")
llm_only = pd.read_csv('results/fact_checking/fact_check_raw_results_llm_only.csv')
print(f"LLM-only: {len(llm_only)} claims")

print("\nLoading LLM+KG results...")
llm_kg = pd.read_csv('results/fact_checking/fact_check_raw_results_llm_kg.csv')
print(f"LLM+KG: {len(llm_kg)} claims")

# 4. Match by position in test dataset
# Assumption: RAG processed claims in order but stopped early
print("\n" + "=" * 60)
print("MATCHING PREDICTIONS BY POSITION")
print("=" * 60)

# Get first N claims that RAG completed
n_rag_complete = len(rag_complete)
print(f"\nTaking first {n_rag_complete} claims from all systems...")

# Match by claim text to be safe
test_data['claim_clean'] = test_data['claim'].str.strip()
llm_only['claim_clean'] = llm_only['claim'].str.strip()
llm_kg['claim_clean'] = llm_kg['claim'].str.strip()

# Merge all
merged = test_data.merge(
    llm_only[['claim_clean', 'true_verdict', 'predicted_verdict']],
    on='claim_clean',
    how='inner',
    suffixes=('', '_llm_only')
).merge(
    llm_kg[['claim_clean', 'true_verdict', 'predicted_verdict']],
    on='claim_clean',
    how='inner',
    suffixes=('_llm_only', '_llm_kg')
)

print(f"Matched claims across LLM-only and LLM+KG: {len(merged)}")

# Take only first N that RAG completed
merged_subset = merged.head(n_rag_complete).copy()

# Add RAG predictions
merged_subset['rag_prediction'] = rag_complete['predicted_verdict'].values


# Normalize verdicts
def normalize_verdict(v):
    v_str = str(v).lower().strip()
    if v_str in ['true', 'false']:
        return v_str
    elif v_str in ['unknown', 'nan', '']:
        return 'unknown'
    else:
        return 'unknown'


merged_subset['ground_truth'] = merged_subset['true_verdict_llm_only'].apply(normalize_verdict)
merged_subset['rag_prediction_norm'] = merged_subset['rag_prediction'].apply(normalize_verdict)
merged_subset['llm_only_prediction'] = merged_subset['predicted_verdict_llm_only'].apply(normalize_verdict)
merged_subset['llm_kg_prediction'] = merged_subset['predicted_verdict_llm_kg'].apply(normalize_verdict)

# Verify ground truth alignment
print("\nVerifying ground truth alignment...")
print(f"First 5 ground truths from RAG: {rag_complete['true_verdict'].head().tolist()}")
print(f"First 5 ground truths from merged: {merged_subset['ground_truth'].head().tolist()}")

# Create comparison files
comp1 = merged_subset[['ground_truth', 'rag_prediction_norm', 'llm_only_prediction']].copy()
comp1.columns = ['ground_truth', 'rag_prediction', 'llm_only_prediction']

comp2 = merged_subset[['ground_truth', 'rag_prediction_norm', 'llm_kg_prediction']].copy()
comp2.columns = ['ground_truth', 'rag_prediction', 'llm_kg_prediction']

comp3 = merged_subset[['ground_truth', 'llm_only_prediction', 'llm_kg_prediction']].copy()

# Save
comp1.to_csv('results/comparison_rag_vs_llm_only_factcheck.csv', index=False)
comp2.to_csv('results/comparison_rag_vs_llm_kg_factcheck.csv', index=False)
comp3.to_csv('results/comparison_llm_only_vs_kg_factcheck.csv', index=False)

print("\n" + "=" * 60)
print("✅ SAVED COMPARISON FILES")
print("=" * 60)
print(f"  Based on {len(comp1)} matched claims")
print("  1. comparison_rag_vs_llm_only_factcheck.csv")
print("  2. comparison_rag_vs_llm_kg_factcheck.csv")
print("  3. comparison_llm_only_vs_kg_factcheck.csv")

# Preview
print("\n" + "=" * 60)
print("PREVIEW (first 10):")
print("=" * 60)
print(comp1.head(10))

# Quick accuracy
from sklearn.metrics import accuracy_score

# Remove 'unknown' predictions for fair comparison
valid_mask = (comp1['rag_prediction'] != 'unknown') & (comp1['llm_only_prediction'] != 'unknown')
valid_comp1 = comp1[valid_mask]

if len(valid_comp1) > 0:
    acc_rag = accuracy_score(valid_comp1['ground_truth'], valid_comp1['rag_prediction'])
    acc_llm_only = accuracy_score(comp3['ground_truth'], comp3['llm_only_prediction'])
    acc_llm_kg = accuracy_score(comp3['ground_truth'], comp3['llm_kg_prediction'])

    print(f"\nAccuracy Preview:")
    print(f"  RAG:       {acc_rag:.3f} ({len(valid_comp1)} valid predictions)")
    print(f"  LLM-only:  {acc_llm_only:.3f}")
    print(f"  LLM+KG:    {acc_llm_kg:.3f}")
else:
    print("\n⚠️  No valid RAG predictions to compare")

print("\n" + "=" * 60)
print("Next step: Run statistical tests")
print("=" * 60)

# Remove empty rows
rag_complete = rag_results[rag_results['true_verdict'].notna()].copy()
print(f"Complete RAG predictions: {len(rag_complete)}")

# 3. Load Christopher's results
print("\nLoading LLM-only results...")
llm_only = pd.read_csv('results/fact_checking/fact_check_raw_results_llm_only.csv')
print(f"LLM-only: {len(llm_only)} claims")

print("\nLoading LLM+KG results...")
llm_kg = pd.read_csv('results/fact_checking/fact_check_raw_results_llm_kg.csv')
print(f"LLM+KG: {len(llm_kg)} claims")

# 4. Match by position in test dataset
# Assumption: RAG processed claims in order but stopped early
print("\n" + "=" * 60)
print("MATCHING PREDICTIONS BY POSITION")
print("=" * 60)

# Get first N claims that RAG completed
n_rag_complete = len(rag_complete)
print(f"\nTaking first {n_rag_complete} claims from all systems...")

# Match by claim text to be safe
test_data['claim_clean'] = test_data['claim'].str.strip()
llm_only['claim_clean'] = llm_only['claim'].str.strip()
llm_kg['claim_clean'] = llm_kg['claim'].str.strip()

# Merge all
merged = test_data.merge(
    llm_only[['claim_clean', 'true_verdict', 'predicted_verdict']],
    on='claim_clean',
    how='inner',
    suffixes=('', '_llm_only')
).merge(
    llm_kg[['claim_clean', 'true_verdict', 'predicted_verdict']],
    on='claim_clean',
    how='inner',
    suffixes=('_llm_only', '_llm_kg')
)

print(f"Matched claims across LLM-only and LLM+KG: {len(merged)}")

# Take only first N that RAG completed
merged_subset = merged.head(n_rag_complete).copy()

# Add RAG predictions
merged_subset['rag_prediction'] = rag_complete['predicted_verdict'].values


# Normalize verdicts
def normalize_verdict(v):
    v_str = str(v).lower().strip()
    if v_str in ['true', 'false']:
        return v_str
    elif v_str in ['unknown', 'nan', '']:
        return 'unknown'
    else:
        return 'unknown'


merged_subset['ground_truth'] = merged_subset['true_verdict_llm_only'].apply(normalize_verdict)
merged_subset['rag_prediction_norm'] = merged_subset['rag_prediction'].apply(normalize_verdict)
merged_subset['llm_only_prediction'] = merged_subset['predicted_verdict_llm_only'].apply(normalize_verdict)
merged_subset['llm_kg_prediction'] = merged_subset['predicted_verdict_llm_kg'].apply(normalize_verdict)

# Verify ground truth alignment
print("\nVerifying ground truth alignment...")
print(f"First 5 ground truths from RAG: {rag_complete['true_verdict'].head().tolist()}")
print(f"First 5 ground truths from merged: {merged_subset['ground_truth'].head().tolist()}")

# Create comparison files
comp1 = merged_subset[['ground_truth', 'rag_prediction_norm', 'llm_only_prediction']].copy()
comp1.columns = ['ground_truth', 'rag_prediction', 'llm_only_prediction']

comp2 = merged_subset[['ground_truth', 'rag_prediction_norm', 'llm_kg_prediction']].copy()
comp2.columns = ['ground_truth', 'rag_prediction', 'llm_kg_prediction']

comp3 = merged_subset[['ground_truth', 'llm_only_prediction', 'llm_kg_prediction']].copy()

# Save
comp1.to_csv('results/comparison_rag_vs_llm_only_factcheck.csv', index=False)
comp2.to_csv('results/comparison_rag_vs_llm_kg_factcheck.csv', index=False)
comp3.to_csv('results/comparison_llm_only_vs_kg_factcheck.csv', index=False)

print("\n" + "=" * 60)
print("✅ SAVED COMPARISON FILES")
print("=" * 60)
print(f"  Based on {len(comp1)} matched claims")
print("  1. comparison_rag_vs_llm_only_factcheck.csv")
print("  2. comparison_rag_vs_llm_kg_factcheck.csv")
print("  3. comparison_llm_only_vs_kg_factcheck.csv")

# Preview
print("\n" + "=" * 60)
print("PREVIEW (first 10):")
print("=" * 60)
print(comp1.head(10))

# Quick accuracy
from sklearn.metrics import accuracy_score

# Remove 'unknown' predictions for fair comparison
valid_mask = (comp1['rag_prediction'] != 'unknown') & (comp1['llm_only_prediction'] != 'unknown')
valid_comp1 = comp1[valid_mask]

if len(valid_comp1) > 0:
    acc_rag = accuracy_score(valid_comp1['ground_truth'], valid_comp1['rag_prediction'])
    acc_llm_only = accuracy_score(comp3['ground_truth'], comp3['llm_only_prediction'])
    acc_llm_kg = accuracy_score(comp3['ground_truth'], comp3['llm_kg_prediction'])

    print(f"\nAccuracy Preview:")
    print(f"  RAG:       {acc_rag:.3f} ({len(valid_comp1)} valid predictions)")
    print(f"  LLM-only:  {acc_llm_only:.3f}")
    print(f"  LLM+KG:    {acc_llm_kg:.3f}")
else:
    print("\n⚠️  No valid RAG predictions to compare")

print("\n" + "=" * 60)
print("Next step: Run statistical tests")
print("=" * 60)