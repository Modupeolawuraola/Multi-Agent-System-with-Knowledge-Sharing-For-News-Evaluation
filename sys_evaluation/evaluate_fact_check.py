import os
import logging
import json
import pandas as pd
from sklearn.metrics import classification_report
from src_v3.memory.schema import GraphState
from src_v3.memory.knowledge_graph import KnowledgeGraph
from src_v3.workflow.simplified_workflow import process_articles
from src_v3.components.fact_checker.fact_checker_updated import fact_checker_agent
from src_v3.components.fact_checker.tools import create_factcheck_chain, initialize_entity_extractor, get_bedrock_llm
from sys_evaluation.metrics_updated import save_fact_check_results
from sys_evaluation.visualization_updated import plot_confusion_matrix


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def normalize_label(label: str) -> str:
    """
    Standardizes label strings for consistency in evaluation.
    Capitalizes and strips whitespace.
    """
    if isinstance(label, str):
        return label.strip().capitalize()
    return "Unknown"

def load_factcheck_dataset():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR, "sys_evaluation", "test_dataset", "fact_check_test.tsv")
    df = pd.read_csv(path, sep='\t', encoding='utf-8')

    df['ground_truth'] = df['rating'].apply(normalize_label)

    claims = []
    for _, row in df.iterrows():
        claims.append({
            "date": row['date'],
            "claim": row['claim'],
            "ground_truth": row['ground_truth']
        })
    return claims

def run_fact_check(articles, knowledge_graph=None, store_to_kg=False):
    graph_state = GraphState(articles=articles, current_status="ready")
    clean_articles = []
    for a in graph_state.articles:
        if isinstance(a, str):
            try:
                a = json.loads(a)
            except Exception as e:
                logging.error(f"Invalid article format: {e}")
                continue
        clean_articles.append(a)

    graph_state.articles = clean_articles
    for i, a in enumerate(clean_articles):
        if "ground_truth" in a:
            a["ground_truth_verdict"] = a["ground_truth"]
    try:
        return fact_checker_agent(graph_state, knowledge_graph, store_to_kg=store_to_kg)
    except Exception as e:
        logging.error(f"Error during fact checking: {e}")
        return GraphState(error=str(e))


def evaluate_factcheck_workflow():
    logging.info("=== FACT CHECKING WORKFLOW EVALUATION ===")

    # Step 1: Load test data
    articles = load_factcheck_dataset()

    # Step 2: Initialize system components
    logging.info("[FULL SYSTEM] LLM + KG fact checking")
    logging.info("[SETUP] Initializing LLM and entity extractor")
    llm = get_bedrock_llm()
    initialize_entity_extractor(llm)
    knowledge_graph = KnowledgeGraph()
    updated_state = run_fact_check(articles, knowledge_graph=knowledge_graph)

    # Step 3: Extract predictions and ground truth
    y_true, y_pred = extract_predictions(updated_state)

    # Step 4: Compute metrics
    logging.info("=== EVALUATION METRICS ===")
    from sklearn.metrics import classification_report, accuracy_score
    report = classification_report(y_true, y_pred, labels=["True", "False"], output_dict=True, zero_division=0)
    accuracy = accuracy_score(y_true, y_pred)

    for label in ["True", "False"]:
        logging.info(f"{label} Precision: {report.get(label, {}).get('precision', 0.0):.3f}")
        logging.info(f"{label} Recall:    {report.get(label, {}).get('recall', 0.0):.3f}")
        logging.info(f"{label} F1-score:  {report.get(label, {}).get('f1-score', 0.0):.3f}")

    logging.info(f"Macro F1:     {report.get('macro avg', {}).get('f1-score', 0.0):.3f}")
    logging.info(f"Weighted F1:  {report.get('weighted avg', {}).get('f1-score', 0.0):.3f}")
    logging.info(f"Accuracy:     {accuracy:.3f}")
    # Step 5: Plot confusion matrix
    plot_confusion_matrix(
        y_true, y_pred,
        labels=["True", "False"],
        title="Fact Checking Confusion Matrix"
    )

    # Step 6: Save results to CSV
    result_rows = []
    for article, truth, pred in zip(updated_state.articles, y_true, y_pred):
        reasoning = ""
        result = article.get("fact_check_result", {})
        if isinstance(result, dict):
            reasoning = result.get("reasoning", "")
        elif isinstance(result, str):
            try:
                parsed = json.loads(result)
                reasoning = parsed.get("reasoning", "")
            except:
                reasoning = ""

        result_rows.append({
            "claim": article.get("claim", ""),
            "true_verdict": truth,
            "predicted_verdict": pred,
            "reasoning": reasoning
        })

    results_df = pd.DataFrame(result_rows)
    results_df.to_csv("sys_evaluation/factcheck_eval_results.csv", index=False)
    logging.info("Saved results to sys_evaluation/factcheck_eval_results.csv")

    return report


def extract_predictions(state):
    y_true = []
    y_pred = []

    for art in state.articles:
        ground_truth = normalize_label(art.get("ground_truth_verdict", ""))

        result_raw = art.get("fact_check_result", {})
        pred = "Unknown"

        if isinstance(result_raw, dict):
            pred = normalize_label(result_raw.get("verdict", "Unknown"))

        elif isinstance(result_raw, str):
            try:
                parsed = json.loads(result_raw)
                pred = normalize_label(parsed.get("verdict", "Unknown"))
            except Exception as e:
                logging.warning(f"Failed to parse fact_check_result string: {e}")

        y_true.append(ground_truth)
        y_pred.append(pred)

    return y_true, y_pred

def safe_evaluate(y_true, y_pred, labels, title="Confusion Matrix"):
    if not any(label in y_true for label in labels):
        logging.warning(f"No valid labels in ground truth for evaluation: {labels}")
        return

    try:
        print(classification_report(y_true, y_pred, labels=labels, zero_division=0))
        plot_confusion_matrix(y_true, y_pred, labels=labels, title=title)
    except Exception as e:
        logging.error(f"Error during evaluation or plotting: {e}")

def benchmark_fact_checking():
    logging.info("== FACT CHECKING BENCHMARK STARTED ==")

    # Load test dataset
    articles = load_factcheck_dataset()
    articles_copy = json.loads(json.dumps(articles))  # Deep copy

    # Baseline: LLM only
    logging.info("[BASELINE] LLM-only fact checking")
    state_baseline = run_fact_check(articles_copy, knowledge_graph=None)

    # KG-enhanced: LLM + KG
    logging.info("[FULL SYSTEM] LLM + KG fact checking")
    state_kg = run_fact_check(articles, knowledge_graph=KnowledgeGraph())

    # Extract predictions
    y_true_baseline, y_pred_baseline = extract_predictions(state_baseline)
    y_true_kg, y_pred_kg = extract_predictions(state_kg)

    # store raw results
    save_fact_check_results("sys_evaluation/raw_results_llm_only.csv", state_baseline.articles, y_true_baseline,
                           y_pred_baseline)
    save_fact_check_results("sys_evaluation/raw_results_llm_kg.csv", state_kg.articles, y_true_kg, y_pred_kg)

    # Calculate metrics
    logging.info("== METRICS ==")
    print("[LLM ONLY]")
    safe_evaluate(y_true_baseline, y_pred_baseline, labels=["True", "False"], title="LLM-only Fact Checking")

    print("[LLM + KG]")
    safe_evaluate(y_true_kg, y_pred_kg, labels=["True", "False"], title="LLM+KG Fact Checking")


if __name__ == "__main__":
    mode = os.environ.get("EVALUATION_MODE", "benchmark")
    if mode == "factcheck":
        evaluate_factcheck_workflow()
    elif mode == "benchmark":
        initialize_entity_extractor(get_bedrock_llm())
        benchmark_fact_checking()
    else:
        print("Unsupported mode. Use EVALUATION_MODE=factcheck or EVALUATION_MODE=benchmark")