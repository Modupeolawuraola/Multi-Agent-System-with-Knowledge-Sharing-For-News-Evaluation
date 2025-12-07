"""
Run statistical tests for bias detection comparison
"""
import pandas as pd
from statistical_testing import add_statistical_significance

print("="*60)
print("BIAS DETECTION - STATISTICAL SIGNIFICANCE TESTING")
print("="*60)

# Load comparison files (created by extract_christopher_predictions.py)
comp1 = pd.read_csv('results/comparison_rag_vs_llm_only_bias.csv')
comp2 = pd.read_csv('results/comparison_rag_vs_llm_kg_bias.csv')


# Extract predictions
y_true = comp1['ground_truth'].tolist()
y_pred_rag = comp1['rag_prediction'].tolist()
y_pred_llm_only = comp1['llm_only_prediction'].tolist()
y_pred_llm_kg = comp2['llm_kg_prediction'].tolist()

print(f"\nTest set size: {len(y_true)} articles")

# Test 1: RAG vs LLM-only
print("\n" + "="*60)
print("TEST 1: RAG vs LLM-only")
print("="*60)
result1 = add_statistical_significance(
    y_true, y_pred_rag, y_pred_llm_only,
    method1_name="RAG",
    method2_name="LLM-only"
)

# Test 2: RAG vs LLM+KG
print("\n" + "="*60)
print("TEST 2: RAG vs LLM+KG")
print("="*60)
result2 = add_statistical_significance(
    y_true, y_pred_rag, y_pred_llm_kg,
    method1_name="RAG",
    method2_name="LLM+KG"
)

# Test 3: LLM-only vs LLM+KG
print("\n" + "="*60)
print("TEST 3: LLM-only vs LLM+KG")
print("="*60)
result3 = add_statistical_significance(
    y_true, y_pred_llm_only, y_pred_llm_kg,
    method1_name="LLM-only",
    method2_name="LLM+KG"
)

print("\n" + "="*60)
print("✅ ALL BIAS DETECTION TESTS COMPLETE!")
print("="*60)