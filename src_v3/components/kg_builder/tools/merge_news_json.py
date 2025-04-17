import json
import glob
import os


def merge_json_files(input_dir, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    json_files = glob.glob(os.path.join(input_dir, "*.json"))

    merged_data = {"status": "ok", "totalResults": 0, "articles": []}

    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "articles" in data:
                merged_data["articles"].extend(data["articles"])
                merged_data["totalResults"] += data.get("totalResults", len(data["articles"]))

    # Deduplicate by URL
    unique_articles = {a["url"]: a for a in merged_data["articles"]}
    merged_data["articles"] = list(unique_articles.values())
    merged_data["totalResults"] = len(merged_data["articles"])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=2)


#
# json_files = glob.glob("news_jsons/archive-3-25_3-31/*.json")
#
# merged_data = {
#     "status": "ok",
#     "totalResults": 0,
#     "articles": []
# }
#
# # Read and merge all JSON files
# for file in json_files:
#     with open(file, "r", encoding="utf-8") as f:
#         data = json.load(f)
#         print(file)
#         if "articles" in data:
#
#             merged_data["articles"].extend(data["articles"])
#             merged_data["totalResults"] += data["totalResults"]
#
# # Remove duplicates based on the article URL
# unique_articles = {article["url"]: article for article in merged_data["articles"]}.values()
# merged_data["articles"] = list(unique_articles)
# merged_data["totalResults"] = len(merged_data["articles"])
#
# # Save the merged JSON data
# with open("../news_jsons/archive-3-25_3-31/all_merged_news3_25-3_31.json", "w", encoding="utf-8") as outfile:
#     json.dump(merged_data, outfile, indent=4)
#
# print("Merged JSON file created: all_merged_news3_25-3_31.json")
#
