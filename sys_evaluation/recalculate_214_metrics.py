"""
Statistical tests on 214 claims (including Misleading)
"""
import pandas as pd
import sys
sys.path.insert(0, '.')
from statistical_testing import add_statistical_significance

print("="*60)
print("STATISTICAL TESTS - 214 CLAIMS (INCLUDING MISLEADING)")
print("="*60)

# Load comparison files (already have 214 claims)
comp1 = pd.read_csv('results/fact_checking/comparison_rag_vs_llm_only_factcheck.csv', dtype=str)
comp2 = pd.read_csv('results/fact_checking/comparison_rag_vs_llm_kg_factcheck.csv', dtype=str)
comp3 = pd.read_csv('results/fact_checking/comparison_llm_only_vs_kg_factcheck.csv', dtype=str)

# NO FILTERING - use all 214 claims
y_true = comp1['ground_truth'].tolist()
y_rag = comp1['rag_prediction'].tolist()
y_llm_only = comp1['llm_only_prediction'].tolist()
y_llm_kg = comp2['llm_kg_prediction'].tolist()

print(f"\nDataset size: {len(y_true)} claims")

# Test 1: RAG vs LLM-only
print("\n" + "="*60)
print("TEST 1: RAG vs LLM-only")
print("="*60)
add_statistical_significance(y_true, y_rag, y_llm_only, "RAG", "LLM-only")

# Test 2: RAG vs LLM+KG
print("\n" + "="*60)
print("TEST 2: RAG vs LLM+KG")
print("="*60)
add_statistical_significance(y_true, y_rag, y_llm_kg, "RAG", "LLM+KG")

# Test 3: LLM-only vs LLM+KG
print("\n" + "="*60)
print("TEST 3: LLM-only vs LLM+KG")
print("="*60)
add_statistical_significance(y_true, y_llm_only, y_llm_kg, "LLM-only", "LLM+KG")

print("\n" + "="*60)
print("✅ ALL TESTS COMPLETE (214 CLAIMS)!")
print("="*60)

