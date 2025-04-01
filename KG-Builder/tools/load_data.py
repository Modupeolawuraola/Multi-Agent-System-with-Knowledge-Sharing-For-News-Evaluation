#%%
import json
from langchain_community.document_loaders import JSONLoader
#%%


# data_loader = JSONLoader(
#     file_path='./political_news_20250217_164112.json',
#     jq_schema='.articles[]',
#     text_content=False
# )


#docs = data_loader.load()

with open('./KG-Builder/political_news_20250217_164112.json', encoding="utf-8") as json_file:
    articles_data = json.load(json_file)
    articles = articles_data['articles']

print(articles_data)
print(type(articles))