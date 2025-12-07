"""
Evaluating RAG Baseline on Bias Detection and Fact-checking
"""
import os
import logging
import sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_baseline.rag_system import RAGBaseline
from metrics_updated import calculate_bias_metrics
from sys_evaluation.visualization_updated import plot_confusion_matrix



logging.basicConfig(level=logging.INFO)

def load_bias_dataset():
    """Load bias test dataset"""
    path = 'test_dataset/bias_cleaned_file.csv'
    df= pd.read_csv(path)
    df['bias'] = df['bias'].str.lower().str.strip()
    df['bias'] = df['bias'].replace({'lean left': 'left', 'lean right': 'right'})

    articles = []
    for _, row in df.iterrows():
        articles.append({
            "title": row['title'],
            "content": row['full_content'],
            "source": row['source_name'],
            "ground_truth_bias": row['bias']

        })
    return articles

def load_factcheck_dataset():
    """Load factcheck test dataset"""
    path = 'test_dataset/fact_check_test.tsv'
    df = pd.read_csv(path, sep='\t')
    df["ground_truth"] = df["rating"].str.strip().str.capitalize()

    claims = []
    for _, row in df.iterrows():
        claims.append({
            "claim": row['claim'],
            "ground_truth": row['ground_truth']
        })
    return claims

def evaluate_rag_bias():
    """Evaluate RAG on bias detection"""
    logging.info("=====RAG BIAS DETECTION EVALUATION=====")

    #LOAD DATA
    articles = load_bias_dataset()

    #split into context articles and text articles
    split_idx = int(len(articles) * 0.8)
    context_articles = articles[:split_idx]
    test_articles = articles[split_idx:]

    logging.info(f"Context articles: {len(context_articles)}")
    logging.info(f"Test articles: {len(test_articles)}")

    #initialize RAG
    rag = RAGBaseline()

    # add context articles
    rag.add_articles_for_bias(context_articles)

    #classify text articles
    y_true =[]
    y_pred =[]

    for article in test_articles:
        result = rag.classify_bias(article)
        y_true.append(article['ground_truth_bias'])
        y_pred.append(result['bias'])

        logging.info(f"Article: {article['title'][:50]}...")
        logging.info(f"True: {article['ground_truth_bias']}, Pred: {result['bias']}")

    #calculate metrics
    metrics = calculate_bias_metrics(y_true, y_pred)

    logging.info("===METRICS====")
    logging.info(f"Weighted F1: {metrics['weighted_f1']}:.3f")
    logging.info(f"Balanced Accuracy: {metrics['balanced_accuracy']}:.3f")
    logging.info(f"Cohen's Kappa: {metrics['cohen_kappa']}:.3f")



    #save results
    result_df =pd.DataFrame({
        'true_bias':y_true,
        'predicted_bias':y_pred

    })
    result_df.to_csv('results/rag__bias_confusion.csv', index=False)

    return metrics

def evaluate_rag_factcheck():
    """Evaluate RAG on factcheck test dataset"""
    logging.info("=====RAG FACTCHECK EVALUATION=====")


    #load claims
    claims = load_factcheck_dataset()

    #load articles for context (reuse bias articles)
    articles = load_bias_dataset()

    #initialize RAG
    rag= RAGBaseline()
    rag.add_articles_for_factcheck(articles)

    #check claims
    y_true =[]
    y_pred =[]

    for claim in claims:
        result = rag.check_fact(claim['claim'])
        y_true.append(claim['ground_truth'])
        y_pred.append(result['verdict'].capitalize())

        logging.info(f"Claim: {claim['claim'][:50]}...")

        logging.info(f"True: {claim['ground_truth']}, Pred: {result['verdict']}")

    #calculate metrics (adapt to match your existing format)
    from sklearn.metrics import classification_report
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    logging.info("====METRICS====")

    logging.info(f"Macro F1: {report['macro avg'] ['f1-score']:.3f}")
    logging.info(f"Weighted F1: {report['weighted avg']['f1-score']:.3f}")



    #save results
    result_df =pd.DataFrame({
        'true_bias':y_true,
        'predicted_bias':y_pred
    })
    result_df.to_csv('results/rag_factcheck_confusion.csv', index=False)
    return report

if __name__ == '__main__':
    # run evaluations
    print("starting RAG Evaluation")
    print("="*60)

    bias_metrics = evaluate_rag_bias()

    print("\n" + "="*60)

    fact_metrics = evaluate_rag_factcheck()

    print("\nRAG evaluation complete")



