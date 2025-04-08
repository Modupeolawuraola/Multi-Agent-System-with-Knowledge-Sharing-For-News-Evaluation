import json
import os
import logging
import csv
from sklearn.metrics import accuracy_score, precision_score, f1_score
import matplotlib.pyplot as plt

from src.memory.schema import GraphState
from src.components.bias_analyzer_agent import bias_analyzer_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def parse_predicted_bias(bias_analysis: dict) -> str:
    """Convert the agent's 'bias_analysis' output to 'left', 'right', 'center', or 'unknown'."""
    if not bias_analysis or 'overall_assessment' not in bias_analysis:
        return "unknown"
    assessment = bias_analysis['overall_assessment'].lower()
    if "left" in assessment:
        return "left"
    elif "right" in assessment:
        return "right"
    elif "neutral" in assessment or "balanced" in assessment or "center" in assessment:
        return "center"
    return "unknown"


def compute_metrics(y_true, y_pred, approach_label=""):
    """
    Example function that logs or calculates
    accuracy, precision, recall, or F1.

    """
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

    logging.info(f"\n=== Metrics for {approach_label} ===")
    logging.info(f"Accuracy: {accuracy:.2f}")

    save_results_to_csv("results.csv", approach_label, accuracy, precision, f1)
    return accuracy, precision, f1


def plot_metrics(y_true, y_pred_full, y_pred_content_only):
    """
    Placeholder for any chart or confusion matrix code.
    """
    labels = ["Accuracy", "Precision", "F1 Score"]

    acc_full, prec_full, f1_full = compute_metrics(y_true, y_pred_full, "Full Context")
    acc_content, prec_content, f1_content = compute_metrics(y_true, y_pred_content_only, "Content-Only")

    # Bar chart data
    full_metrics = [acc_full, prec_full, f1_full]
    content_metrics = [acc_content, prec_content, f1_content]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for i, metric in enumerate(labels):
        axes[i].bar(["Full Context", "Content-Only"], [full_metrics[i], content_metrics[i]], color=['blue', 'green'])
        axes[i].set_title(metric)
        axes[i].set_ylim(0, 1)
        axes[i].set_ylabel("Score")

    plt.tight_layout()
    plt.savefig("bias_detection_benchmark.png")
    plt.show()

def filter_json(input_json_path: str):
    """
    Loads a JSON file, removes articles with "Unknown" bias, and saves the filtered JSON.
    """
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    filtered_articles = []

    for article in data["articles"]:
        bias = article["bias"]

        # Standardize bias labels
        if bias == "Lean Left":
            bias = "Left"
        elif bias == "Lean Right":
            bias = "Right"

        # Only keep articles that are not "Unknown"
        if bias != "Unknown":
            article["bias"] = bias  # Update bias label
            filtered_articles.append(article)

    data["articles"] = filtered_articles

    return filtered_articles

def evaluate_bias_analyzer_full_vs_content(articles: list[dict]):
    """
    Evaluates the bias_analyzer_agent's ability to classify news bias using:
      1. Full context (source, author, content)
      2. Content-only (just the article text)
    """
    y_true = []
    y_pred_full = []
    y_pred_content_only = []

    for i, article in enumerate(articles):
        true_bias = article.get("bias", "unknown")
        y_true.append(true_bias)

        raw_source = article.get("source", {})

        # Log what it originally is:
        print(f"Before normalization, article #{i} source is:", type(raw_source), raw_source)

        # Determine the text: prefer full_content if available, else fall back to content
        article_text = (article.get("full_content") or "").strip()
        if not article_text:
            article_text = article.get("content", "").strip()

        raw_source = article.get("source", {})
        if isinstance(raw_source, str):
            # Convert a string like "CNN" into a dictionary
            # so your chain can do .items() or ["name"]
            raw_source = {"id": "unknown", "name": raw_source}

        elif not isinstance(raw_source, dict):
            # If it's something unexpected (None, int, etc.), fallback
            raw_source = {"id": "unknown", "name": "unknown"}
        article["source"] = raw_source

        print(f"After normalization, article #{i} source is:", type(article["source"]), article["source"])

        ########################################
        # 1) Evaluate with FULL CONTEXT
        ########################################
        full_context_article = {
            "title": article.get("title", ""),
            "content": article_text,
            # Include source & author here
            "source": article["source"],
            "author": article.get("author", "")
        }

        # Build a GraphState with just this article
        full_context_state = GraphState(articles=[full_context_article])
        analyzed_full = bias_analyzer_agent(full_context_state)

        # There's exactly one article in the returned state
        full_analysis = analyzed_full.articles[0].get("bias_analysis", {})
        full_label = parse_predicted_bias(full_analysis)
        y_pred_full.append(full_label)

        ########################################
        # 2) Evaluate with CONTENT ONLY
        ########################################
        content_only_article = {
            "title": article.get("title", ""),
            "content": article_text

        }

        content_only_state = GraphState(articles=[content_only_article])
        analyzed_content_only = bias_analyzer_agent(content_only_state)

        content_only_analysis = analyzed_content_only.articles[0].get("bias_analysis", {})
        content_only_label = parse_predicted_bias(content_only_analysis)
        y_pred_content_only.append(content_only_label)

        # Logging / Debug
        logging.info(f"Article #{i + 1} | Title: {article.get('title', '')[:60]}")
        logging.info(f"Ground Truth: {true_bias}")
        logging.info(f"  Full Context Prediction   : {full_label}")
        logging.info(f"  Content-Only Prediction  : {content_only_label}")

    # Compute metrics
    compute_metrics(y_true, y_pred_full, "Full Context (Source + Author + Content)")
    compute_metrics(y_true, y_pred_content_only, "Content-Only")

    # Optionally plot or compare
    plot_metrics(y_true, y_pred_full, y_pred_content_only)


def evaluate_bias_analyzer_on_json(json_path: str):
    """
    Loads the JSON file (with top-level 'articles'),
    then calls evaluate_bias_analyzer_full_vs_content()
    to measure how the agent performs under both conditions.
    """
    os.environ["EVALUATION_MODE"] = "true"

    # with open(json_path, "r", encoding="utf-8") as infile:
    #     data = json.load(infile)
    #
    # articles_data = data.get("articles", [])
    # if not articles_data:
    #     logging.warning(f"No articles found in {json_path}!")
    #     return
    #
    # logging.info(f"Loaded {len(articles_data)} articles from {json_path}")
    filter_articles = filter_json(json_path)

    # Run the two-approach evaluation
    evaluate_bias_analyzer_full_vs_content(filter_articles)

def save_results_to_csv(file_path, method_name, accuracy, precision, f1):
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)

        # Write header if the file is new
        if not file_exists:
            writer.writerow(["Method", "Accuracy", "Precision", "F1 Score"])

        writer.writerow([method_name, accuracy, precision, f1])

if __name__ == "__main__":

    path_to_json = ("test_dataset/final_news_4_01_to_4_05_with_bias.json")
    # filter_articles = filter_json(path_to_json)
    evaluate_bias_analyzer_on_json(path_to_json)
