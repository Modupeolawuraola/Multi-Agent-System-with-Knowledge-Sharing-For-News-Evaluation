import json
import pandas as pd
import re


def clean_name(name):
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"(?<=news) digital", "", name, flags=re.IGNORECASE)
    name = name.lower()
    name = re.sub(r'[^a-z0-9 ]+', '', name)
    name = re.sub(r'\\s+', ' ', name).strip()
    return name

def build_bias_map(allsides_csv):
    # e.g. CSV columns: ["Source", "Bias"]
    df = pd.read_csv(allsides_csv)
    bias_map = {}
    for idx, row in df.iterrows():
        raw_name = row["allsides_media_bias_ratings/publication/source_name"]
        cleaned = clean_name(raw_name)
        bias_map[cleaned] = row["allsides_media_bias_ratings/publication/media_bias_rating"]
    return bias_map


    if best:
        match_str, score, _ = best
        if score >= threshold:
            return bias_map[match_str]
    return 'Unknown'

def add_bias_to_json(
    news_json_path: str,
    allsides_csv_file: str,
    output_json_path: str
):
    """
    Reads a JSON file in the NewsAPI format and an AllSides CSV with columns like:
        Source, Bias
    Merges the bias label into each article, matching by article['source']['name'].
    Writes a new JSON file with an added 'bias' field per article.
    """

    # 1. Load the JSON
    with open(news_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    articles = data.get('articles', [])

    bias_map = build_bias_map(allsides_csv_file)

    # 2. Load the AllSides CSV -> create a dict { 'ABC News': 'Center', ... }
    df = pd.read_csv(allsides_csv_file)
    bias_dict = dict(zip(df['allsides_media_bias_ratings/publication/source_name'], df['allsides_media_bias_ratings/publication/media_bias_rating']))

    # 3. Add bias to each article
    for article in articles:
        raw_source_name = article['source'].get('name', '')
        cleaned_source_name = clean_name(raw_source_name)
        bias = bias_map.get(cleaned_source_name, 'Unknown')  # default if no match
        article['bias'] = bias

    # 4. Write the updated JSON
    with open(output_json_path, 'w', encoding='utf-8') as out:
        json.dump(data, out, indent=2, ensure_ascii=False)


def select_json_articles(input_json_path, output_json_path, max_articles=100):
    """
    Reads 'input_json_path', keeps only the first `max_articles` in the
    'articles' list, and writes out to 'output_json_path'.
    """
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if 'articles' in data:
        data['articles'] = data['articles'][:max_articles]

    with open(output_json_path, 'w', encoding='utf-8') as out:
        json.dump(data, out, indent=2, ensure_ascii=False)

if __name__ == '__main__':

    add_bias_to_json(
        news_json_path='../news_jsons/archive-3-25_3-31/all_merged_news3_25-3_31.json',
        allsides_csv_file='./AllSides Media Bias Ratings 3.11.25.csv',
        output_json_path='../news_jsons/archive-3-25_3-31/all_articles_3_25-3_31_with_bias.json'
    )
    print('Merged AllSides bias info into JSON. Saved as all_articles_3_25-3_31_with_bias.json')



