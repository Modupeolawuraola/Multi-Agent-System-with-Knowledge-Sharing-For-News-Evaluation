import json
import csv


def json_to_csv(json_input_path, csv_output_path):
    with open(json_input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract the list of articles
    articles = data.get('articles', [])

    # Define the CSV headers
    headers = [
        'source_id', 'source_name', 'author', 'title', 'description',
        'url', 'urlToImage', 'publishedAt', 'content', 'full_content', 'bias'
    ]

    # Open the CSV file for writing
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        # Write each article's data to the CSV
        for article in articles:
            source_id = article.get('source', {}).get('id', '')
            source_name = article.get('source', {}).get('name', '')

            writer.writerow([
                source_id,
                source_name,
                article.get('author', ''),
                article.get('title', ''),
                article.get('description', ''),
                article.get('url', ''),
                article.get('urlToImage', ''),
                article.get('publishedAt', ''),
                article.get('content', ''),
                article.get('full_content', ''),
                article.get('bias', '')
            ])


if __name__ == '__main__':
    json_to_csv('../../tests/test_dataset/final_news_4_01_to_4_05_with_bias.json', 'test_bias_4_01_to_4_05.csv')
    print("Conversion complete! Check 'test_bias_4_01_to_4_05.csv'.")
