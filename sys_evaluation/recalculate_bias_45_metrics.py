"""
Recalculate bias metrics from the 45 matched articles
"""
import pandas as pd
from sklearn.metrics import classification_report

print("="*60)
print("RECALCULATING BIAS METRICS (45 MATCHED ARTICLES)")
print("="*60)

# Load comparison files
comp1 = pd.read_csv('results/bias_classification/comparison_rag_vs_llm_only_bias.csv')
comp2 = pd.read_csv('results/bias_classification/comparison_rag_vs_llm_kg_bias.csv')
comp3 = pd.read_csv('results/bias_classification/comparison_llm_only_vs_kg_bias.csv')

# Get predictions
y_true = comp1['ground_truth'].tolist()
y_rag = comp1['rag_prediction'].tolist()
y_llm_only = comp1['llm_only_prediction'].tolist()
y_llm_kg = comp2['llm_kg_prediction'].tolist()

print(f"\nDataset size: {len(y_true)} articles")

# Calculate for each method
print("\n" + "="*60)
print("RAG METRICS")
print("="*60)
rag_report = classification_report(y_true, y_rag, labels=['left', 'center', 'right'],
                                   output_dict=True, zero_division=0)
print(classification_report(y_true, y_rag, labels=['left', 'center', 'right'], zero_division=0))

print("\n" + "="*60)
print("LLM-ONLY METRICS")
print("="*60)
llm_only_report = classification_report(y_true, y_llm_only, labels=['left', 'center', 'right'],
                                       output_dict=True, zero_division=0)
print(classification_report(y_true, y_llm_only, labels=['left', 'center', 'right'], zero_division=0))

print("\n" + "="*60)
print("LLM+KG METRICS")
print("="*60)
llm_kg_report = classification_report(y_true, y_llm_kg, labels=['left', 'center', 'right'],
                                     output_dict=True, zero_division=0)
print(classification_report(y_true, y_llm_kg, labels=['left', 'center', 'right'], zero_division=0))

# Print summary for tables
print("\n" + "="*60)
print("SUMMARY FOR TABLES")
print("="*60)

print("\n━━━ RAG ━━━")
print(f"Weighted F1: {rag_report['weighted avg']['f1-score']:.3f}")
print(f"Balanced Acc: {rag_report['macro avg']['recall']:.3f}")
print(f"Macro F1: {rag_report['macro avg']['f1-score']:.3f}")

print("\n━━━ LLM-Only ━━━")
print(f"Weighted F1: {llm_only_report['weighted avg']['f1-score']:.3f}")
print(f"Balanced Acc: {llm_only_report['macro avg']['recall']:.3f}")
print(f"Macro F1: {llm_only_report['macro avg']['f1-score']:.3f}")

print("\n━━━ LLM+KG ━━━")
print(f"Weighted F1: {llm_kg_report['weighted avg']['f1-score']:.3f}")
print(f"Balanced Acc: {llm_kg_report['macro avg']['recall']:.3f}")
print(f"Macro F1: {llm_kg_report['macro avg']['f1-score']:.3f}")