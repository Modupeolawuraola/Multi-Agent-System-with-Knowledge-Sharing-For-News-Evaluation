import os, json
import boto3
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import accuracy_score, precision_score, f1_score
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

def load_data(csv_file):
    df = pd.read_csv(csv_file)
    if 'statement' not in df.columns or 'target' not in df.columns:
        raise ValueError("CSV must contain 'statement' and 'label' columns.")

    label_mapping = {
        'true': 'True',
        'mostly-true': 'True',
        'barely-true': 'False',
        'false': 'False',
        'pants-fire': 'False'
    }
    df['target'] = df['target'].map(label_mapping)

    df = df.dropna(subset=['target'])
    return df

def fact_check(statement, llm):
    prompt = f"""Evaluate the factual accuracy of the following statement. 
    Respond with only 'True' or 'False'. 
    Statement: {statement}"""

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        answer = response.content.strip()
    else:
        answer = str(response).strip()

    return answer if answer in ["True", "False"] else "False"


def plot_metrics(accuracy, precision, f1):
    metrics = ['Accuracy', 'Precision', 'F1 Score']
    values = [accuracy, precision, f1]

    plt.figure(figsize=(8, 5))
    plt.bar(metrics, values, color=['blue', 'green', 'red'])
    plt.ylim(0, 1)
    plt.xlabel("Metrics")
    plt.ylabel("Score")
    plt.title("Evaluation Metrics for Fact-Checking LLM")
    plt.show()

def evaluate_model(csv_file):
    df = load_data(csv_file)
    llm = create_llm()
    df['predicted'] = df['statement'].apply(lambda x: fact_check(x, llm))

    df['target'] = df['target'].astype(str)
    accuracy = accuracy_score(df['target'], df['predicted'])
    precision = precision_score(df['target'], df['predicted'], pos_label="True")
    f1 = f1_score(df['target'], df['predicted'], pos_label="True")

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"F1 Score: {f1:.4f}")

    plot_metrics(accuracy, precision, f1)

    return df

url = 'https://raw.githubusercontent.com/Modupeolawuraola/Multi-Agent-System-with-Knowledge-Sharing-For-News-Evaluation/refs/heads/overall-code-review/sys_evaluation/test_dataset/politifact_general_news.csv?token=GHSAT0AAAAAAC5K326KRJZXKR3WY4YO6LSCZ6XTLRA'

evaluate_model(url)