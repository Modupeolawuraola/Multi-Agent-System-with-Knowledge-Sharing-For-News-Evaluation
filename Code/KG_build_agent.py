import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from retry import retry
from string import Template
import json
from neo4j import GraphDatabase
from py2neo import Graph, Node, Relationship
from newsapi import NewsApiClient
import glob
from timeit import default_timer as timer
from dotenv import load_dotenv
from time import sleep
from huggingface_hub import login
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)

load_status = load_dotenv('.env')
if load_status is False:
    raise RuntimeError('Environment variables not loaded.')

# Neo4j config
URI = os.getenv('NEO4J_URI')
AUTH = (os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))


with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection established.")
graph = Graph(URI, auth=AUTH)

# Set up LLM
tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3.5-mini-instruct", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3.5-mini-instruct",
                                             trust_remote_code=True).to(device)
# model.to('cuda')
#login(os.getenv('LLM_TOKEN'))

# Define function to process inputs
# def process_llm(file_prompt, system_msg):
#     messages = [
#         {'role': 'system', 'content': system_msg},
#         {'role': 'user', 'content': file_prompt}
#     ]
#
#     prompt = f'<s>[INST] {system_msg} [/INST] {file_prompt} </s>'
#
#     inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096).to('cuda')
#     output_ids = model.generate(**inputs, max_new_tokens=1500, temperature=0)
#
#     nlp_results = tokenizer.decode(output_ids[0], skip_special_tokens=True)
#
#     return nlp_results

def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=500)
    print(f'Generated response input {inputs}')
    print(f'Generated response output {outputs}')
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# funtion to take json of news articles and a prompt template, and return a json-object of all the entities and relationships
def extract_entities_relationships(article):
    prompt = f"""
        You are an IT and database expert who extracts structured knowledge from news articles.
        Given the following article, extract:
        - Entities (people, organizations, events)
        - Relationships between entities
        
        Return ONLY valid JSON output.
    
        ARTICLE:
        Title: "{article['title']}"
        Source: {article['source']['name']}
        Author: {article.get('author', 'Unknown')}
        Published At: {article['publishedAt']}
        Content: {article['content']}
        
        Do not return the prompt, only the json
        """

    structured_data = generate_response(prompt)
    print(f'Json output ================== {structured_data}')
    return json.loads(structured_data)

def store_in_neo4j(structured_data):
    data = structured_data
    for person in data["entities"]["people"]:
        graph.merge(Node("Person", name=person), "Person", "name")

    for org in data["entities"]["organizations"]:
        graph.merge(Node("Organization", name=org), "Organization", "name")

    for event in data["entities"]["events"]:
        graph.merge(Node("Event", name=event), "Event", "name")

        # Create Relationships
    for relation in data["relationships"]:
        source_node = graph.nodes.match(name=relation["source"]).first()
        target_node = graph.nodes.match(name=relation["target"]).first()
        if source_node and target_node:
            rel = Relationship(source_node, relation["relation"].upper(), target_node)
            graph.merge(rel)


def process_news_json(news_json):
    """
    Takes a JSON object containing multiple articles, processes each one with an LLM,
    and stores structured knowledge in Neo4j.
    """
    articles = news_json["articles"]

    for article in articles:
        try:
            structured_data = extract_entities_relationships(article)  # LLM processes article
            store_in_neo4j(structured_data)  # Store processed data in Neo4j
        except Exception as e:
            print(f"Error processing article: {article['title']}\n{e}")

    return {"status": "Knowledge graph updated"}


with open("political_news_20250217_164112.json", "r", encoding="utf-8") as f:
    news_data = json.load(f)

process_news_json(news_data)
