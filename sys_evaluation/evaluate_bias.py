import time
import json
import sys
import os
import logging
import pandas as pd
from src_v3.utils.aws_helpers import diagnostic_check

# Adding the root directory to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from src_v3.memory.schema import GraphState
from src_v3.memory.knowledge_graph import KnowledgeGraph
from sys_evaluation.metrics_updated import (
    calculate_bias_metrics,
    calculate_fact_check_metrics
)
from sys_evaluation.visualization_updated import generate_evaluation_chart, plot_confusion_matrix
from src_v3.workflow.simplified_workflow import process_articles
from src_v3.utils.aws_helpers import get_bedrock_llm
# Import for direct query route
# from src_v3.components.fact_checker.fact_checker_Agent import FactCheckerAgent
# from src_v3.components.fact_checker.fact_checker_updated import FactCheckerAgent, fact_checker_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("evaluation.log"),
        logging.StreamHandler()
    ]
)


def load_bias_dataset():
    """Loading pre-labeled test articles"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
    DATASET_PATH = os.path.join(BASE_DIR, 'sys_evaluation', 'test_dataset', 'bias_cleaned_file.csv')

    # Load from CSV file
    df = pd.read_csv(DATASET_PATH)
    df['bias'] = df['bias'].str.lower().str.strip()
    df['bias'] = df['bias'].replace({
        'lean left': 'left',
        'lean right': 'right'
    })


    # Convert DataFrame rows to article dictionaries
    test_articles = []
    for _, row in df.iterrows():
        article = {
            "title": row['title'],
            "content": row['full_content'],
            "source": row['source_name'],
            "date": row['publishedAt'],
            "url": row['url'],
            # Ground truth labels for evaluation
            'ground_truth_bias': row['bias']
        }
        test_articles.append(article)

    return test_articles


def evaluate_bias_workflow():
    logging.info("=== BIAS DETECTION WORKFLOW EVALUATION ===")

    # Step 1: Load test data
    articles = load_bias_dataset()

    # Step 2: Initialize system components
    graph = KnowledgeGraph()
    graph_state = GraphState(articles=articles, current_status="ready")

    # Step 3: Run bias detection workflow
    updated_state = process_articles(graph_state, knowledge_graph=graph)

    # Step 4: Extract predictions and ground truth
    y_true = []
    y_pred = []

    for article in updated_state.articles:
        ground = article.get("ground_truth_bias", "").lower()
        result = article.get("bias_result")

        if isinstance(result, dict):
            pred = result.get("bias", "").lower()
        elif isinstance(result, str):
            try:
                parsed = json.loads(result)
                pred = parsed.get("bias", "").lower()
            except Exception:
                pred = "unknown"
        else:
            pred = "unknown"

        y_true.append(ground)
        y_pred.append(pred)

    # Step 5: Compute metrics
    logging.info("=== EVALUATION METRICS ===")
    metrics = calculate_bias_metrics(y_true, y_pred)
    for k, v in metrics.items():
        logging.info(f"{k}: {v:.3f}")

    # Step 6: Plot confusion matrix
    plot_confusion_matrix(y_true, y_pred, labels=["left", "center", "right"], title="Bias Detection Confusion Matrix")

    # Step 7: Save results in csv file
    result_rows = []
    for article, truth, pred in zip(updated_state.articles, y_true, y_pred):
        result_rows.append({
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "source": article.get("source", ""),
            "true_bias": truth,
            "predicted_bias": pred,
            "bias_reasoning": article.get("bias_result", {}).get("reasoning", "")
        })

    results_df = pd.DataFrame(result_rows)

    results_df.to_csv("bias_eval_results.csv", index=False)
    logging.info("Saved results to bias_eval_results.csv")


    return metrics



def benchmark_bias_detection(articles):
    logging.info("=== BENCHMARKING: LLM vs LLM+KG ===")

    # --- Step 1: Setup ---
    graph_state = GraphState(articles=articles, current_status="ready")
    articles_copy = json.loads(json.dumps(articles))  # Deep copy to avoid contamination

    # --- Step 2: LLM-only baseline ---
    logging.info("[BASELINE] Evaluating with LLM only (no KG)...")
    baseline_state = process_articles(GraphState(articles=articles_copy), knowledge_graph=None, use_kg=False)

    # --- Step 3: LLM+KG full system ---
    logging.info("[FULL SYSTEM] Evaluating with KG-enhanced context...")
    full_state = process_articles(GraphState(articles=articles), knowledge_graph=KnowledgeGraph())

    # --- Step 4: Extract predictions ---
    def get_predictions(state):
        y_true, y_pred = [], []
        for art in state.articles:
            truth = art.get("ground_truth_bias", "").strip().lower()
            pred_raw = art.get("bias_result")
            pred = "unknown"

            # Case 1: Dict
            if isinstance(pred_raw, dict):
                pred = pred_raw.get("bias", "unknown").strip().lower()

            # Case 2: LangChain Output object with .content
            elif hasattr(pred_raw, "content"):
                try:
                    parsed = json.loads(pred_raw.content)
                    pred = parsed.get("bias", "unknown").strip().lower()
                except Exception as e:
                    logging.warning(f"Failed to parse bias_result.content: {e}")

            # Case 3: JSON string
            elif isinstance(pred_raw, str):
                try:
                    parsed = json.loads(pred_raw)
                    pred = parsed.get("bias", "unknown").strip().lower()
                except Exception as e:
                    logging.warning(f"Failed to parse bias_result string: {e}")

            y_true.append(truth)
            y_pred.append(pred)

        return y_true, y_pred

    y_true_baseline, y_pred_baseline = get_predictions(baseline_state)
    y_true_kg, y_pred_kg = get_predictions(full_state)

    # --- Step 5: Calculate metrics ---
    metrics_baseline = calculate_bias_metrics(y_true_baseline, y_pred_baseline)
    metrics_kg = calculate_bias_metrics(y_true_kg, y_pred_kg)

    # --- Step 6: Print comparison ---
    logging.info("=== METRICS COMPARISON ===")
    for metric in sorted(metrics_baseline.keys()):
        base = metrics_baseline[metric]
        kg = metrics_kg[metric]

        if isinstance(base, dict) or isinstance(kg, dict):
            logging.info(f"{metric:>20}: complex metric (see CSV or nested report)")
        else:
            logging.info(f"{metric:>20}:  LLM-only = {base:.3f}  |  LLM+KG = {kg:.3f}")

    # --- Step 7: Save predictions and confusion matrices ---
    comparison_rows = []
    for art_base, art_kg, y_true in zip(baseline_state.articles, full_state.articles, y_true_kg):
        title = art_kg.get("title", "")
        url = art_kg.get("url", "")
        source = art_kg.get("source", "")
        truth = y_true

        base_raw = art_base.get("bias_result")
        kg_raw = art_kg.get("bias_result")

        base_result = extract_bias_from_result(base_raw)
        kg_result = extract_bias_from_result(kg_raw)

        if isinstance(base_result, str):
            try:
                base_result = json.loads(base_result)
            except:
                base_result = {}
        if isinstance(kg_result, str):
            try:
                kg_result = json.loads(kg_result)
            except:
                kg_result = {}

        comparison_rows.append({
            "title": title,
            "url": url,
            "source": source,
            "true_bias": truth,
            "llm_only_prediction": base_result.get("bias", ""),
            "llm_only_reasoning": base_result.get("reasoning", ""),
            "llm_kg_prediction": kg_result.get("bias", ""),
            "llm_kg_reasoning": kg_result.get("reasoning", "")
        })

    comparison_df = pd.DataFrame(comparison_rows)
    comparison_df.to_csv("bias_benchmark_comparison.csv", index=False)
    logging.info("Saved benchmark comparison to bias_benchmark_comparison.csv")

    # --- Step 8: Save confusion matrices ---
    from sys_evaluation.visualization_updated import plot_confusion_matrix

    plot_confusion_matrix(
        y_true_baseline, y_pred_baseline,
        labels=["left", "center", "right"],
        title="LLM-only Confusion Matrix",
        filename="results/bias_classification/bias_detect_llm_only_confusion_matrix.png"
    )

    plot_confusion_matrix(
        y_true_kg, y_pred_kg,
        labels=["left", "center", "right"],
        title="LLM + KG Confusion Matrix",
        filename="results/bias_classification/bias_detect_llm_kg_confusion_matrix.png"
    )

    return metrics_baseline, metrics_kg



def extract_bias_from_result(result_obj) -> dict:
    """Safely extract the bias dict from LLM output (AIMessage, string, or dict)."""
    if isinstance(result_obj, dict):
        return result_obj

    elif hasattr(result_obj, "content"):  # likely an AIMessage
        try:
            return json.loads(result_obj.content)
        except Exception:
            return {}

    elif isinstance(result_obj, str):
        try:
            return json.loads(result_obj)
        except Exception:
            return {}

    return {}


if __name__ == "__main__":
    mode = os.environ.get("EVALUATION_MODE", "benchmark")
    if mode == "bias":
        evaluate_bias_workflow()
    elif mode == "benchmark":
        articles = load_bias_dataset()
        benchmark_bias_detection(articles)
    else:
        print("Unsupported mode. Use EVALUATION_MODE=bias or EVALUATION_MODE=benchmark")