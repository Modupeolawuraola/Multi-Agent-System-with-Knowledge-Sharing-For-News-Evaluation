
import os
from dotenv import load_dotenv
env_path = os.path.join('..', '.env')
load_dotenv(env_path)
from tools.generate_news_json_from_api import get_dates_between, get_news_json_from_api
from tools.merge_news_json import merge_json_files
from tools.allsides_datagen import add_bias_to_json

def run_news_pipeline(start_date, end_date, allsides_csv_path, output_dir="news_jsons", bias_output_file="final_news_with_bias.json"):
    archive_dir = os.path.join(output_dir, f"archive-{start_date.replace('-', '_')}_{end_date.replace('-', '_')}")
    os.makedirs(archive_dir, exist_ok=True)

    # Step 1: Fetch articles per day in the date range
    dates = get_dates_between(start_date, end_date)
    for date_str in dates:
        daily_file = os.path.join(archive_dir, f"news_{date_str}.json")
        get_news_json_from_api(
            api_url=os.getenv("NEWS_API_URL"),
            api_key=os.getenv("NEWS_API_KEY"),
            date=date_str,
            output_file=daily_file,
            max_results=100
        )

    # Step 2: Merge all JSON files
    merged_file_path = os.path.join(archive_dir, f"merged_news_{start_date}_to_{end_date}.json")
    merge_json_files(input_dir=archive_dir, output_path=merged_file_path)

    # Step 3: Add bias labels
    add_bias_to_json(
        news_json_path=merged_file_path,
        allsides_csv_file=allsides_csv_path,
        output_json_path=bias_output_file
    )

    print(f"Final output with bias saved to: {bias_output_file}")


if __name__ == "__main__":
    run_news_pipeline(
        start_date="2025-04-06",
        end_date="2025-04-14",
        allsides_csv_path="./tools/AllSides Media Bias Ratings 3.11.25.csv",
        bias_output_file="news_jsons/main_corpus/final_news_4_06_to_4_14_with_bias.json"
    )
