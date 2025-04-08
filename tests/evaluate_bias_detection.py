import os
import csv
import logging
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, f1_score

# -- Import your pipeline and components --
from src.main import run_workflow
from src.components.bias_analyzer_agent import bias_analyzer_agent
from src.memory.knowledge_graph import KnowledgeGraph
from src.memory.schema import GraphState

###############################################################################
# Logging Setup
###############################################################################
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

###############################################################################
# Utility Functions
###############################################################################

def parse_predicted_bias(bias_analysis: dict) -> str:
    """
    Convert the agent's 'bias_analysis' output to one of
    ['left', 'right', 'center', 'unknown'].
    """
    if not bias_analysis or 'overall_assessment' not in bias_analysis:
        return "unknown"
    assessment = bias_analysis['overall_assessment'].lower()

    if "left" in assessment:
        return "left"
    elif "right" in assessment:
        return "right"
    elif ("neutral" in assessment or
          "balanced" in assessment or
          "center" in assessment):
        return "center"
    return "unknown"


def standardize_bias_label(bias_str: str) -> str:
    """
    Example to convert labels like "Lean Left" -> "left",
    "Lean Right" -> "right", etc.
    Returns 'unknown' for anything not recognized.
    """
    if not bias_str:
        return "unknown"

    bias_str_lower = bias_str.lower().strip()

    if "left" in bias_str_lower:
        return "left"
    elif "right" in bias_str_lower:
        return "right"
    elif "center" in bias_str_lower or "neutral" in bias_str_lower:
        return "center"
    return "unknown"


def compute_metrics(y_true, y_pred, approach_label=""):
    """
    Calculate and log accuracy, precision, and F1.
    """
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

    logging.info(f"\n=== Metrics for {approach_label} ===")
    logging.info(f"Accuracy:  {accuracy:.2f}")
    logging.info(f"Precision: {precision:.2f}")
    logging.info(f"F1 Score:  {f1:.2f}")

    return accuracy, precision, f1


def plot_metrics(results):
    """
    Create bar charts comparing the accuracy, precision, and F1 across approaches.
    `results` is a dict of the form:
        {
           (approach_name, context_label): (acc, prec, f1),
           ...
        }
    Example approach_name: "Multi-Agent Workflow", "Bias Agent"
    Example context_label: "Full", "Content"
    """
    approaches = sorted(set(k[0] for k in results.keys()))
    contexts   = sorted(set(k[1] for k in results.keys()))
    metrics_list = ["Accuracy", "Precision", "F1 Score"]

    # Organize data
    metric_values = {m: {} for m in metrics_list}
    for (approach, context), (acc, prec, f1) in results.items():
        metric_values["Accuracy"][(approach, context)] = acc
        metric_values["Precision"][(approach, context)] = prec
        metric_values["F1 Score"][(approach, context)] = f1

    # Plot each metric in a separate figure
    for metric in metrics_list:
        plt.figure(figsize=(8,6))
        x_labels = []
        bar_values = []
        for approach in approaches:
            for context in contexts:
                x_labels.append(f"{approach}\n({context})")
                bar_values.append(metric_values[metric].get((approach, context), 0))

        plt.bar(x_labels, bar_values)
        plt.ylim([0, 1])
        plt.title(f"{metric} Comparison")
        plt.ylabel(metric)
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        plt.show()


###############################################################################
# Core Evaluation Logic
###############################################################################
def evaluate_bias(csv_path: str):
    """
    1) Load CSV data.
    2) Filter out articles with 'unknown' bias.
    3) Compare:
       (a) The entire multi-agent system (via run_workflow)
       (b) The individual bias detection agent (via bias_analyzer_agent)
    4) Compare both on:
       - Full context (source_name, author, plus text)
       - Content only (just the text)
    """
    # Step 1: Read CSV
    articles_data = []
    with open(csv_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            row_dict = {
                "source_id": row["source_id"],
                "source_name": row["source_name"],
                "author": row["author"],
                "title": row["title"],
                "content": row["content"],
                "full_content": row["full_content"],
                "bias": standardize_bias_label(row["bias"])
            }
            articles_data.append(row_dict)

    # Step 2: Filter unknown bias
    filtered_articles = [a for a in articles_data if a["bias"] != "unknown"]
    if not filtered_articles:
        logging.warning("No valid articles found after filtering unknown biases.")
        return

    logging.info(f"Loaded {len(filtered_articles)} articles with known bias.")

    # Optional: Instantiate or load your knowledge graph, if needed
    # (depends on how your code uses KnowledgeGraph)
    knowledge_graph = KnowledgeGraph()  # Placeholder usage

    y_true = []
    predictions = {
        "Multi-Agent Workflow": {
            "Full": [],
            "Content": []
        },
        "Bias Agent": {
            "Full": [],
            "Content": []
        }
    }

    # Step 3: Evaluate each approach and each context
    for article in filtered_articles:
        true_bias = article["bias"]
        y_true.append(true_bias)

        # Grab article text
        article_text = (article.get("full_content") or "").strip()
        if not article_text:
            article_text = article.get("content", "").strip()

        # Build an input_data dict if your `run_workflow` expects it
        full_input_data = {
            "articles": [
                {
                    "title": article["title"],
                    "content": article_text,
                    "source": {
                        "id": article["source_id"],
                        "name": article["source_name"]
                    },
                    "author": article["author"]
                }
            ]
        }
        content_only_input_data = {
            "articles": [
                {
                    "title": article["title"],
                    "content": article_text
                    # no source or author
                }
            ]
        }

        # 3a) Multi-Agent Workflow (Full)
        full_state = run_workflow(full_input_data)
        # Suppose your multi-agent pipeline places bias analysis
        # in final_state.articles[i]['bias_analysis']
        # We just pick the first article's analysis
        if full_state.articles and 'bias_analysis' in full_state.articles[0]:
            ma_full_label = parse_predicted_bias(full_state.articles[0]['bias_analysis'])
        else:
            ma_full_label = "unknown"
        predictions["Multi-Agent Workflow"]["Full"].append(ma_full_label)

        # 3b) Multi-Agent Workflow (Content Only)
        content_state = run_workflow(content_only_input_data)
        if content_state.articles and 'bias_analysis' in content_state.articles[0]:
            ma_content_label = parse_predicted_bias(content_state.articles[0]['bias_analysis'])
        else:
            ma_content_label = "unknown"
        predictions["Multi-Agent Workflow"]["Content"].append(ma_content_label)

        # 3c) Individual Bias Agent (Full)
        #    We'll build a GraphState and call bias_analyzer_agent directly
        full_graph_state = GraphState(articles=[
            {
                "title": article["title"],
                "content": article_text,
                "source": {
                    "id": article["source_id"],
                    "name": article["source_name"]
                },
                "author": article["author"]
            }
        ])
        agent_full_result = bias_analyzer_agent(full_graph_state)
        if agent_full_result["articles"] and 'bias_analysis' in agent_full_result["articles"][0]:
            agent_full_label = parse_predicted_bias(agent_full_result["articles"][0]['bias_analysis'])
        else:
            agent_full_label = "unknown"
        predictions["Bias Agent"]["Full"].append(agent_full_label)

        # 3d) Individual Bias Agent (Content Only)
        content_graph_state = GraphState(articles=[
            {
                "title": article["title"],
                "content": article_text
            }
        ])
        agent_content_result = bias_analyzer_agent(content_graph_state)
        if agent_content_result["articles"] and 'bias_analysis' in agent_content_result["articles"][0]:
            agent_content_label = parse_predicted_bias(agent_content_result["articles"][0]['bias_analysis'])
        else:
            agent_content_label = "unknown"
        predictions["Bias Agent"]["Content"].append(agent_content_label)

    # Step 4: Compute and log metrics
    results = {}
    for approach in predictions:
        for context in predictions[approach]:
            y_pred = predictions[approach][context]
            label = f"{approach} - {context}"
            acc, prec, f1 = compute_metrics(y_true, y_pred, label)
            results[(approach, context)] = (acc, prec, f1)

    # Step 5: Optional: Plot the results
    plot_metrics(results)

###############################################################################
# Standalone Entry Point
###############################################################################
if __name__ == "__main__":
    os.environ["EVALUATION_MODE"] = "true"
    path_to_csv = "./test_dataset/test_bias_4_01_to_4_05.csv"
    evaluate_bias(path_to_csv)
