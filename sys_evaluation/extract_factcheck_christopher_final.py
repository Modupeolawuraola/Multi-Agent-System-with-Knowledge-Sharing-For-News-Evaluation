"""
Extract Christopher's fact-checking predictions for the 214 clean claims
"""
import pandas as pd

print("="*60)
print("EXTRACTING CHRISTOPHER'S FACT-CHECKING PREDICTIONS")
print("="*60)

# 1. Load clean test dataset (214 claims)
clean_test = pd.read_csv('test_dataset/fact_check_test_CLEAN.tsv', sep='\t')
print(f"\nClean test dataset: {len(clean_test)} claims")

# 2. Load Christopher's results (229 claims each)
llm_only = pd.read_csv('results/fact_checking/fact_check_raw_results_llm_only.csv')
llm_kg = pd.read_csv('results/fact_checking/fact_check_raw_results_llm_kg.csv')

print(f"Christopher LLM-only: {len(llm_only)} claims")
print(f"Christopher LLM+KG: {len(llm_kg)} claims")

# 3. Match by claim text
clean_test['claim_clean'] = clean_test['claim'].str.strip()
llm_only['claim_clean'] = llm_only['claim'].str.strip()
llm_kg['claim_clean'] = llm_kg['claim'].str.strip()

# 4. Merge to find matching claims
merged = clean_test.merge(
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

print(f"\nMatched claims: {len(merged)}")

# 5. Load YOUR RAG results
rag_results = pd.read_csv('results/FINAL_RESULTS_DEC14/rag_factcheck_confusion_new_2.csv')
print(f"Your RAG results: {len(rag_results)}")

# Verify lengths match
if len(merged) != len(rag_results):
    print(f"\n⚠️  WARNING: Length mismatch!")
    print(f"Christopher matched: {len(merged)}, RAG: {len(rag_results)}")
else:
    print("✅ Lengths match!")

# 6. Normalize verdicts
def normalize_verdict(v):
    #convert boolean to string first
    if isinstance(v, bool):
        v= 'True' if v else 'False'

    v_str = str(v).lower().strip()

    #capitalize properly
    if v_str.lower() in ['true', 'false', 'misleading']:
        return v_str.capitalize()
    else:
        return 'Unknown'

# Create comparison dataframes
comparison_data = pd.DataFrame({
    'ground_truth': merged['true_verdict_llm_only'].apply(normalize_verdict),
    'rag_prediction': rag_results['predicted_bias'].apply(normalize_verdict),
    'llm_only_prediction': merged['predicted_verdict_llm_only'].apply(normalize_verdict),
    'llm_kg_prediction': merged['predicted_verdict_llm_kg'].apply(normalize_verdict)
})

# 7. Save comparison files
comp1 = comparison_data[['ground_truth', 'rag_prediction', 'llm_only_prediction']]
comp2 = comparison_data[['ground_truth', 'rag_prediction', 'llm_kg_prediction']]
comp3 = comparison_data[['ground_truth', 'llm_only_prediction', 'llm_kg_prediction']]

#convert all columns to string to prevent boolean conversion
for col in comp1.columns:
    comp1[col] = comp1[col].astype(str)
for col in comp2.columns:
    comp2[col] = comp2[col].astype(str)
for col in comp3.columns:
    comp3[col] = comp3[col].astype(str)

comp1.to_csv('results/comparison_rag_vs_llm_only_factcheck.csv', index=False, quoting=1)
comp2.to_csv('results/comparison_rag_vs_llm_kg_factcheck.csv', index=False, quoting= 1)
comp3.to_csv('results/comparison_llm_only_vs_kg_factcheck.csv', index=False, quoting =1)

"""

The `quoting=1` will save the CSV like this:

"ground_truth","llm_kg_prediction"
"False","False"
"True","True"

"""
print("\n" + "="*60)
print("✅ SAVED COMPARISON FILES")
print("="*60)
print("  1. comparison_rag_vs_llm_only_factcheck.csv")
print("  2. comparison_rag_vs_llm_kg_factcheck.csv")
print("  3. comparison_llm_only_vs_kg_factcheck.csv")

# Preview
print("\n" + "="*60)
print("PREVIEW (first 10):")
print("="*60)
print(comp1.head(10))

# Quick accuracy
from sklearn.metrics import accuracy_score

acc_rag = accuracy_score(comp1['ground_truth'], comp1['rag_prediction'])
acc_llm_only = accuracy_score(comp3['ground_truth'], comp3['llm_only_prediction'])
acc_llm_kg = accuracy_score(comp3['ground_truth'], comp3['llm_kg_prediction'])

print(f"\nAccuracy Preview:")
print(f"  RAG:       {acc_rag:.3f}")
print(f"  LLM-only:  {acc_llm_only:.3f}")
print(f"  LLM+KG:    {acc_llm_kg:.3f}")