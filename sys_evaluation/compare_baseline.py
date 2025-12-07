import logging

from transformers.models.esm.openfold_utils import permute_final_dims

import pandas as pd
import json
from evaluate_bias import load_bias_dataset, benchmark_bias_detection
from evaluate_rag import  evaluate_rag_bias
from statistical_testing import add_statistical_significant
from metrics_updated import  calculate_bias_metrics
logging.basicConfig(level=logging.INFO)

"""
Compare all the three system : LLM-only , RAG AND llm+ kg
Generate tables and statistical significant tests

"""

def compare_all_system_bias():
    """
    Compare all three system on bias detection:
    1.llm only
    2.RAG(LLM + Vector retrieval)
    3. LLM + KG( the overall system)
    """
    logging.info("==== COMPARING ALL SYSTEM: BIAS DETECTION ====\n")

    #load dataset
    articles = load_bias_dataset()

    #run all three evaluations
    logging.info("Running LLM and LLM+ KG benchmarks......")
    metrics_baseline, metrics_kg= benchmark_bias_detection(articles)

    logging.info("\nRunning RAG evaluation.....")
    metrics_rag = evaluate_rag_bias()

    #create comparison table
    comparison= {
        'Metric': ['Balanced Accuracy', 'Cohen Kappa', 'Macro F1', 'MCC', 'Weighted F1'],
        'LLM-only':[
            metrics_baseline['balanced_accuracy'],
            metrics_baseline['cohen_kappa'],
            metrics_baseline['macro_f1'],
            metrics_baseline['mcc'],
            metrics_baseline['weighted_f1']
        ],
        'RAG':[
            metrics_rag['balanced_accuracy'],
            metrics_rag['cohen_kappa'],
            metrics_rag['macro_f1'],
            metrics_rag['mcc'],
            metrics_rag['weighted_f1']
        ],
        'LLM+KG':[
            metrics_baseline['balanced_accuracy'],
            metrics_baseline['cohen_kappa'],
            metrics_baseline['macro_f1'],
            metrics_baseline['mcc'],
            metrics_baseline['weighted_f1']
        ]
    }

    df = p.DataFrame(comparison)
    print("\n====BIAS DETECTION COMPARISON=====\n")
    print(df.to_string(index=False))

    #save to csa
    df.to_csv('sys_evaluation/result/bias_comparison_all_systems.csv', index=False)
    logging.info("\nSaved comparison to sys_evaluation/result/bias_comparison_all_systems.csv")

    #3. statistical significance testing
    #we will need to get the y_true and y_pred for each system
    #this is simplified and easier to adapt based on actual evaluation results
    return {
        'llm_only':metrics_baseline,
        'rag': metrics_rag,
        "llm_kg":metrics_kg

    }
if __name__ =="__main__":
    results = compare_all_system_bias()