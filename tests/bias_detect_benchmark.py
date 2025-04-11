import os, json
import torch
import boto3
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import accuracy_score, precision_score, f1_score
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
from langchain_aws import ChatBedrock


load_dotenv()
env_path = os.path.join('..', '.env')
load_dotenv(env_path)

def create_bedrock_client():
    """Create bedrock authenticated Bedrock client"""
    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("aws_access_key_id"),
            aws_secret_access_key=os.getenv("aws_secret_access_key"),
            aws_session_token=os.getenv('aws_session_token'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        bedrock_client= session.client(service_name='bedrock-runtime',
                                       region_name=os.getenv('AWS_REGION', 'us-east-1')
                                       )
        return bedrock_client
    except Exception as e:
        print(f"Error creating bedrock client: {e}")
        raise

def create_llm():
    """Create Bedrock LLm Instance"""
    try:
        client = create_bedrock_client()
        #initialize anthropic calude model through bedrock

        llm= ChatBedrock(
            client= client,
            model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_kwargs={
                "max_tokens":4096,
                "temperature":0.2,
                "top_p":0.9
            }
        )
        return llm
    except Exception as e:
        print(f"Error initializing Bedrock LLM: {e}")
        raise

def call_claude(llm, prompt: str) -> str:
    """
    Calls AWS Bedrock's Claude model to classify news bias.
    Uses the pre-initialized LLM instance.
    """
    try:
        response = llm.invoke(prompt)
        if hasattr(response, "content"):
            return response.content.strip()
        else:
            return str(response).strip()

    except Exception as e:
        print(f"Error calling Claude: {e}")
        return "Unknown"

def filter_json(input_json_path: str, output_json_path: str):
    """
    Loads a JSON file, removes articles with "Unknown" bias, and saves the filtered JSON.
    """
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    filtered_articles = []

    for article in data["articles"]:
        bias = article["bias"]

        if bias not in ["Left", "Lean Left", "Right", "Lean Right", "Center"]:
            bias = "Unknown"
        # Standardize bias labels
        # if bias == "Lean Left":
        #     bias = "Left"
        # elif bias == "Lean Right":
        #     bias = "Right"

        # Only keep articles that are not "Unknown"
        if bias != "Unknown":
            article["bias"] = bias  # Update bias label
            filtered_articles.append(article)

    data["articles"] = filtered_articles
    with open(output_json_path, 'w', encoding='utf-8') as out:
        json.dump(data, out, indent=2, ensure_ascii=False)

    print(f"Filtered JSON saved: {output_json_path} (Total articles: {len(filtered_articles)})")
    return filtered_articles

def evaluate_llm(articles: list[dict], llm):
    """
    Evaluates Claude's ability to classify news bias using:
    1. Full context (source, author, content)
    2. Content-only
    """
    y_true = []
    y_pred_full = []
    y_pred_content_only = []

    for article in articles:
        true_bias = article["bias"]
        y_true.append(true_bias)

        article_text = article.get("full_content", "").strip()
        if not article_text:
            article_text = article.get("content", "").strip()

        # Generate input prompts
        full_context_prompt = f"""
        Classify the political bias of the following news article.
        Source: {article['source']['name']}
        Author: {article['author']}
        Content: {article_text}
        Categories: Left, Lean Left, Right, Lean Right, Center.
        Answer with only the category name.
        """

        content_only_prompt = f"""
        Classify the political bias of the following news article.
        Content: {article_text}
        Categories: Left, Lean Left, Right, Lean Right, Center.
        Answer with only the category name.
        """

        # Call Claude for bias classification
        pred_full = call_claude(llm, full_context_prompt)
        pred_content_only = call_claude(llm, content_only_prompt)

        y_pred_full.append(pred_full)
        y_pred_content_only.append(pred_content_only)

    # Compute metrics
    compute_metrics(y_true, y_pred_full, "Full Context (Source + Author + Content)")
    compute_metrics(y_true, y_pred_content_only, "Content-Only")

    # Plot results
    plot_metrics(y_true, y_pred_full, y_pred_content_only)

def compute_metrics(y_true, y_pred, method_name):
    """
    Computes accuracy, precision, and F1-score.
    """
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

    print(f"\n=== Evaluation Results: {method_name} ===")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, zero_division=0))

    return accuracy, precision, f1

def plot_metrics(y_true, y_pred_full, y_pred_content_only):
    """
    Plots Accuracy, Precision, and F1-score.
    """
    labels = ["Accuracy", "Precision", "F1 Score"]

    # Compute metrics
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

def main():
    input_json = "./test_dataset/all_articles_3_25-3_31_with_bias_for_test.json"
    filtered_json = "filtered_articles.json"

    # Step 1: Remove articles with "Unknown" bias
    filtered_articles = filter_json(input_json, filtered_json)

    # Step 2: Initialize AWS Bedrock LLM (Claude)
    llm = create_llm()

    # Step 3: Evaluate Claude bias detection
    evaluate_llm(filtered_articles, llm)

if __name__ == "__main__":
    main()