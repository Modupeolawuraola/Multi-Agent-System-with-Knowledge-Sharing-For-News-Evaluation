import os
from dotenv import load_dotenv
from src_v2.components.kg_builder.kg_builder import KnowledgeGraph


def run_news_pipeline(start_date, end_date, allsides_csv_path=None, output_dir="news_jsons", bias_output_file=None):
    """
    Run the news pipeline to fetch, merge, and add bias to articles

    Args:
        start_date: Starting date in YYYY-MM-DD format
        end_date: Ending date in YYYY-MM-DD format
        allsides_csv_path: Path to AllSides Media Bias CSV (optional)
        output_dir: Directory to save JSON files
        bias_output_file: Output file for the final JSON with bias
    """
    # Initialize KG
    kg = KnowledgeGraph()

    # Create archive directory
    archive_dir = os.path.join(output_dir, f"archive-{start_date.replace('-', '_')}_{end_date.replace('-', '_')}")
    os.makedirs(archive_dir, exist_ok=True)

    # Fetch and process articles
    articles = kg.fetch_news_for_daterange(
        start_date=start_date,
        end_date=end_date,
        query="politics",
        output_dir=archive_dir
    )

    # If bias output file is specified and AllSides CSV exists, add bias data
    if bias_output_file and allsides_csv_path and os.path.exists(allsides_csv_path):
        import pandas as pd

        # Load AllSides bias data
        allsides_df = pd.read_csv(allsides_csv_path)

        # Process each article to add bias
        for article in articles:
            source = article.get('source')
            if source:
                # Look up source in AllSides data
                bias_match = allsides_df[allsides_df['News Source'].str.lower() == source.lower()]
                if not bias_match.empty:
                    bias_rating = bias_match.iloc[0]['Bias Rating']
                    article['bias'] = {
                        'source': 'AllSides',
                        'rating': bias_rating
                    }

        # Save final output with bias
        with open(bias_output_file, 'w', encoding='utf-8') as f:
            import json
            json.dump({'articles': articles}, f, indent=2)

        print(f"Final output with bias saved to: {bias_output_file}")

    return articles


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    run_news_pipeline(
        start_date="2025-04-01",
        end_date="2025-04-05",
        allsides_csv_path="./AllSides Media Bias Ratings 3.11.25.csv",
        bias_output_file="news_jsons/final_news_with_bias.json"
    )