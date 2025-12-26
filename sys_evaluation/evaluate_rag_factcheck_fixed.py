"""
Re-run RAG fact-checking evaluation with INCREMENTAL SAVING
This prevents data loss if the process crashes
"""
import os
import logging
import sys
import pandas as pd
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_baseline.rag_system import RAGBaseline

logging.basicConfig(level=logging.INFO)


def load_bias_dataset():
    """Load bias articles for context"""
    path = 'test_dataset/bias_cleaned_file.csv'
    df = pd.read_csv(path)"""
Re-run RAG fact-checking evaluation with INCREMENTAL SAVING
This prevents data loss if the process crashes
"""
import os
import logging
import sys
import pandas as pd
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_baseline.rag_system import RAGBaseline

logging.basicConfig(level=logging.INFO)


def load_bias_dataset():
    """Load bias articles for context"""
    path = 'test_dataset/bias_cleaned_file.csv'
    df = pd.read_csv(path)

    articles = []
    for _, row in df.iterrows():
        articles.append({
            "title": row['title'],
            "content": row['full_content'],
            "source": row['source_name']
        })
    return articles


def load_factcheck_dataset():
    """Load factcheck test dataset"""
    path = 'test_dataset/fact_check_test_CLEAN.tsv'
    df = pd.read_csv(path, sep='\t')
    df["ground_truth"] = df["rating"].str.strip().str.capitalize()

    claims = []
    for _, row in df.iterrows():
        claims.append({
            "claim": row['claim'],
            "ground_truth": row['ground_truth']
        })
    return claims


def evaluate_rag_factcheck_incremental():
    """
    Evaluate RAG on fact-checking with INCREMENTAL SAVING
    Saves after each prediction so we don't lose progress
    """
    logging.info("=" * 60)
    logging.info("RAG FACT-CHECKING EVALUATION (INCREMENTAL)")
    logging.info("=" * 60)

    # Output file
    output_file = 'results/rag_factcheck_confusion_new.csv'
    progress_file = 'results/rag_factcheck_progress.json'

    # Check if we're resuming from a previous run
    start_idx = 0
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
            start_idx = progress.get('last_completed_idx', 0) + 1
        logging.info(f"Resuming from claim {start_idx}")

    # Load data
    claims = load_factcheck_dataset()
    articles = load_bias_dataset()

    logging.info(f"Total claims to process: {len(claims)}")
    logging.info(f"Starting from claim: {start_idx}")

    # Initialize RAG
    logging.info("Initializing RAG system...")
    rag = RAGBaseline()
    rag.add_articles_for_factcheck(articles)

    # Create or load existing results
    if os.path.exists(output_file) and start_idx > 0:
        results_df = pd.read_csv(output_file)
        results = results_df.to_dict('records')
    else:
        results = []

    # Process claims
    for idx in range(start_idx, len(claims)):
        claim_obj = claims[idx]

        try:
            # Check fact
            result = rag.check_fact(claim_obj['claim'])

            # Normalize verdict
            verdict = result['verdict'].capitalize()
            if verdict not in ['True', 'False']:
                verdict = 'Unknown'

            # Store result
            results.append({
                'true_bias': claim_obj['ground_truth'],
                'predicted_bias': verdict
            })

            # Save incrementally (every prediction)
            temp_df = pd.DataFrame(results)
            temp_df.to_csv(output_file, index=False)

            # Update progress
            with open(progress_file, 'w') as f:
                json.dump({
                    'last_completed_idx': idx,
                    'timestamp': datetime.now().isoformat()
                }, f)

            # Log progress
            if idx % 10 == 0 or idx == len(claims) - 1:
                logging.info(
                    f"Progress: {idx + 1}/{len(claims)} claims processed ({(idx + 1) / len(claims) * 100:.1f}%)")

            logging.info(f"Claim {idx + 1}: {claim_obj['claim'][:50]}...")
            logging.info(f"  True: {claim_obj['ground_truth']}, Pred: {verdict}")

        except Exception as e:
            logging.error(f"Error processing claim {idx}: {e}")
            # Save error but continue
            results.append({
                'true_bias': claim_obj['ground_truth'],
                'predicted_bias': 'Error'
            })
            temp_df = pd.DataFrame(results)
            temp_df.to_csv(output_file, index=False)
            continue

    # Final save
    final_df = pd.DataFrame(results)
    final_df.to_csv(output_file, index=False)

    # Calculate metrics
    from sklearn.metrics import classification_report

    y_true = final_df['true_bias'].tolist()
    y_pred = final_df['predicted_bias'].tolist()

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    logging.info("\n" + "=" * 60)
    logging.info("FINAL METRICS")
    logging.info("=" * 60)
    logging.info(f"Macro F1: {report['macro avg']['f1-score']:.3f}")
    logging.info(f"Weighted F1: {report['weighted avg']['f1-score']:.3f}")

    # Clean up progress file
    if os.path.exists(progress_file):
        os.remove(progress_file)

    logging.info(f"\n✅ Results saved to: {output_file}")
    logging.info(f"✅ Total claims processed: {len(results)}")

    return report


if __name__ == '__main__':
    print("=" * 60)
    print("RE-RUNNING RAG FACT-CHECKING EVALUATION")
    print("=" * 60)
    print("\nFeatures:")
    print("  - Incremental saving (won't lose progress if it crashes)")
    print("  - Can resume from where it stopped")
    print("  - Better error handling")
    print("\nEstimated time: 3-5 days on CPU")
    print("=" * 60)

    input("\nPress Enter to start...")

    fact_metrics = evaluate_rag_factcheck_incremental()

    print("\n" + "=" * 60)
    print("✅ RAG FACT-CHECKING EVALUATION COMPLETE!")
    print("=" * 60)

    articles = []
    for _, row in df.iterrows():
        articles.append({
            "title": row['title'],
            "content": row['full_content'],
            "source": row['source_name']
        })
    return articles


def load_factcheck_dataset():
    """Load factcheck test dataset"""
    path = 'test_dataset/fact_check_test_CLEAN.tsv'
    df = pd.read_csv(path, sep='\t')
    df["ground_truth"] = df["rating"].str.strip().str.capitalize()

    claims = []
    for _, row in df.iterrows():
        claims.append({
            "claim": row['claim'],
            "ground_truth": row['ground_truth']
        })
    return claims


def evaluate_rag_factcheck_incremental():
    """
    Evaluate RAG on fact-checking with INCREMENTAL SAVING
    Saves after each prediction so we don't lose progress
    """
    logging.info("=" * 60)
    logging.info("RAG FACT-CHECKING EVALUATION (INCREMENTAL)")
    logging.info("=" * 60)

    # Output file
    output_file = 'results/rag_factcheck_confusion_new.csv'
    progress_file = 'results/rag_factcheck_progress.json'

    # Check if we're resuming from a previous run
    start_idx = 0
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
            start_idx = progress.get('last_completed_idx', 0) + 1
        logging.info(f"Resuming from claim {start_idx}")

    # Load data
    claims = load_factcheck_dataset()
    articles = load_bias_dataset()

    logging.info(f"Total claims to process: {len(claims)}")
    logging.info(f"Starting from claim: {start_idx}")

    # Initialize RAG
    logging.info("Initializing RAG system...")
    rag = RAGBaseline()
    rag.add_articles_for_factcheck(articles)

    # Create or load existing results
    if os.path.exists(output_file) and start_idx > 0:
        results_df = pd.read_csv(output_file)
        results = results_df.to_dict('records')
    else:
        results = []

    # Process claims
    for idx in range(start_idx, len(claims)):
        claim_obj = claims[idx]

        try:
            # Check fact
            result = rag.check_fact(claim_obj['claim'])

            # Normalize verdict
            verdict = result['verdict'].capitalize()
            if verdict not in ['True', 'False']:
                verdict = 'Unknown'

            # Store result
            results.append({
                'true_bias': claim_obj['ground_truth'],
                'predicted_bias': verdict
            })

            # Save incrementally (every prediction)
            temp_df = pd.DataFrame(results)
            temp_df.to_csv(output_file, index=False)

            # Update progress
            with open(progress_file, 'w') as f:
                json.dump({
                    'last_completed_idx': idx,
                    'timestamp': datetime.now().isoformat()
                }, f)

            # Log progress
            if idx % 10 == 0 or idx == len(claims) - 1:
                logging.info(
                    f"Progress: {idx + 1}/{len(claims)} claims processed ({(idx + 1) / len(claims) * 100:.1f}%)")

            logging.info(f"Claim {idx + 1}: {claim_obj['claim'][:50]}...")
            logging.info(f"  True: {claim_obj['ground_truth']}, Pred: {verdict}")

        except Exception as e:
            logging.error(f"Error processing claim {idx}: {e}")
            # Save error but continue
            results.append({
                'true_bias': claim_obj['ground_truth'],
                'predicted_bias': 'Error'
            })
            temp_df = pd.DataFrame(results)
            temp_df.to_csv(output_file, index=False)
            continue

    # Final save
    final_df = pd.DataFrame(results)
    final_df.to_csv(output_file, index=False)

    # Calculate metrics
    from sklearn.metrics import classification_report

    y_true = final_df['true_bias'].tolist()
    y_pred = final_df['predicted_bias'].tolist()

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    logging.info("\n" + "=" * 60)
    logging.info("FINAL METRICS")
    logging.info("=" * 60)
    logging.info(f"Macro F1: {report['macro avg']['f1-score']:.3f}")
    logging.info(f"Weighted F1: {report['weighted avg']['f1-score']:.3f}")

    # Clean up progress file
    if os.path.exists(progress_file):
        os.remove(progress_file)

    logging.info(f"\n✅ Results saved to: {output_file}")
    logging.info(f"✅ Total claims processed: {len(results)}")

    return report


if __name__ == '__main__':
    print("=" * 60)
    print("RE-RUNNING RAG FACT-CHECKING EVALUATION")
    print("=" * 60)
    print("\nFeatures:")
    print("  - Incremental saving (won't lose progress if it crashes)")
    print("  - Can resume from where it stopped")
    print("  - Better error handling")
    print("\nEstimated time: 3-5 days on CPU")
    print("=" * 60)

    input("\nPress Enter to start...")

    fact_metrics = evaluate_rag_factcheck_incremental()

    print("\n" + "=" * 60)
    print("✅ RAG FACT-CHECKING EVALUATION COMPLETE!")
    print("=" * 60)