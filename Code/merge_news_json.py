import json
import glob


json_files = glob.glob("./news_jsons/*.json")

merged_data = {
    "status": "ok",
    "totalResults": 0,
    "articles": []
}

# Read and merge all JSON files
for file in json_files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        print(file)
        if "articles" in data:

            merged_data["articles"].extend(data["articles"])
            merged_data["totalResults"] += data["totalResults"]

# Remove duplicates based on the article URL
unique_articles = {article["url"]: article for article in merged_data["articles"]}.values()
merged_data["articles"] = list(unique_articles)
merged_data["totalResults"] = len(merged_data["articles"])

# Save the merged JSON data
with open("merged_news2_25-3_24.json", "w", encoding="utf-8") as outfile:
    json.dump(merged_data, outfile, indent=4)

print("Merged JSON file created: merged_news2_25-3_24.json.json")
