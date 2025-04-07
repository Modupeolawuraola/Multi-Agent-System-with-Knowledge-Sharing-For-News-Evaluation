import pandas as pd
import json
import os


os.makedirs('sys_evaluation/test_dataset/', exist_ok=True)

# Load the dataset
df = pd.read_csv('sys_evaluation/test_dataset/politifact_general_news.csv')


# Better handling of PolitiFact ratings to create bias and fact labels
def get_fact_rating(rating):
    # Map PolitiFact ratings to boolean truth values and confidence
    rating_map = {
        'true': {'is_true': True, 'confidence': 1.0},
        'mostly-true': {'is_true': True, 'confidence': 0.8},
        'half-true': {'is_true': True, 'confidence': 0.5},
        'barely-true': {'is_true': False, 'confidence': 0.2},
        'false': {'is_true': False, 'confidence': 0.0},
        'pants-fire': {'is_true': False, 'confidence': 0.0}
    }

    if rating.lower() in rating_map:
        return rating_map[rating.lower()]
    return {'is_true': False, 'confidence': 0.0}  # Default


def get_bias_label(rating, source):
    # Simple heuristic for bias detection
    # This is just an example -
    if rating.lower() in ['pants-fire', 'false']:
        if 'social media' in source.lower() or 'facebook' in source.lower():
            return 'right-biased'
        return 'biased'
    elif rating.lower() in ['barely-true']:
        return 'slightly-biased'
    elif rating.lower() in ['half-true']:
        return 'neutral'
    else:
        return 'factual'


# Transform the data to match expected format
evaluation_data = []
for _, row in df.iterrows():
    # Get fact rating
    fact_rating = get_fact_rating(row['target'])

    # Get bias label
    bias_label = get_bias_label(row['target'], row['source'])

    # Create structured entry for evaluation
    entry = {
        'title': f"Fact check: {row['statement'][:50]}...",  # Create title from statement
        'content': row['statement'],  # The full statement is the content
        'source': row['source'],
        'date': row['date'],
        'url': 'https://example.com/fact-check',  # Placeholder URL
        'bias_label': bias_label,  # Generate bias label
        'fact_claims': json.dumps([{
            'claim': row['statement'],
            'is_true': fact_rating['is_true'],
            'confidence': fact_rating['confidence']
        }])
    }
    evaluation_data.append(entry)

# Create a DataFrame and save to CSV
eval_df = pd.DataFrame(evaluation_data)
eval_df.to_csv('sys_evaluation/test_dataset/news_evaluation_data.csv', index=False)

print(f"Converted {len(evaluation_data)} articles to the evaluation format.")