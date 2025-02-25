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
import re
#
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(device)
#
# load_status = load_dotenv('.env')
# if load_status is False:
#     raise RuntimeError('Environment variables not loaded.')
#
# # Neo4j config
# URI = os.getenv('NEO4J_URI')
# AUTH = (os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
#
#
# with GraphDatabase.driver(URI, auth=AUTH) as driver:
#     driver.verify_connectivity()
#     print("Connection established.")
# graph = Graph(URI, auth=AUTH)
#
# # Set up LLM
# tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3.5-mini-instruct", trust_remote_code=True)
# model = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3.5-mini-instruct",
#                                              trust_remote_code=True).to(device)
#
#
# def generate_response(prompt):
#     inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
#     outputs = model.generate(**inputs, max_new_tokens=500)
#     response = tokenizer.decode(outputs[0], skip_special_tokens=True)
#
#     answer_match = re.search(r'### Answer\s*', response)
#     if answer_match:
#         response = response[answer_match.end():]
#
#     json_match = re.search(r'\{(?:[^{}]|(?R))*\}', response, re.DOTALL)
#     if json_match:
#         raw_json = json_match.group(0)
#         try:
#             sanitized_json = re.sub(r'\{\s*\.\.\.\s*\}', '{}', raw_json).strip()
#             return json.loads(sanitized_json)
#         except json.JSONDecodeError as e:
#             print(f"Failed to parse JSON. Raw output:\n{raw_json}\nError: {e}")
#             raise ValueError("Invalid JSON format returned by LLM.")
#     else:
#         raise ValueError("No valid JSON found in LLM response.")
#
#         #
#         # ARTICLE:
#         # Title: "{article['title']}"
#         # Source: {article['source']['name']}
#         # Author: {article.get('author', 'Unknown')}
#         # Published At: {article['publishedAt']}
#         # Content: {article['content']}
#         #
#
# # funtion to take json of news articles and a prompt template, and return a json-object of all the entities and relationships
# def extract_entities_relationships(article):
#     prompt = f"""
#         You are an IT and database expert who extracts structured knowledge from news articles.
#         Given the following article, extract:
#         - Entities (people, organizations, events)
#         - Relationships between entities
#
#         **Return only a valid JSON object** without explanations, placeholders (e.g., `{{...}}`), or extra text.
#         Ensure correct formatting and valid field names.
#
#             Expected JSON output example:
#         {{
#             "entities": [
#                 {{"type": "person", "name": "John Doe"}},
#                 {{"type": "organization", "name": "M23 rebels"}}
#             ],
#             "relationships": [
#                 {{"source": "Rwanda", "relation": "supports", "target": "M23 rebels"}}
#             ]
#         }}
#
#         """
#
#     structured_data = generate_response(prompt)
#     print(f'Json output ================== {structured_data}')
#     return json.loads(structured_data)
#
# def store_in_neo4j(structured_data):
#     data = structured_data
#     for person in data["entities"]["people"]:
#         graph.merge(Node("Person", name=person), "Person", "name")
#
#     for org in data["entities"]["organizations"]:
#         graph.merge(Node("Organization", name=org), "Organization", "name")
#
#     for event in data["entities"]["events"]:
#         graph.merge(Node("Event", name=event), "Event", "name")
#
#         # Create Relationships
#     for relation in data["relationships"]:
#         source_node = graph.nodes.match(name=relation["source"]).first()
#         target_node = graph.nodes.match(name=relation["target"]).first()
#         if source_node and target_node:
#             rel = Relationship(source_node, relation["relation"].upper(), target_node)
#             graph.merge(rel)
#
#
# def process_news_json(news_json):
#     """
#     Takes a JSON object containing multiple articles, processes each one with an LLM,
#     and stores structured knowledge in Neo4j.
#     """
#     articles = news_json["articles"]
#
#     for article in articles:
#         try:
#             structured_data = extract_entities_relationships(article)  # LLM processes article
#             store_in_neo4j(structured_data)  # Store processed data in Neo4j
#         except Exception as e:
#             print(f"Error processing article: {article['title']}\n{e}")
#
#     return {"status": "Knowledge graph updated"}
#
#
# with open("political_news_20250217_164112.json", "r", encoding="utf-8") as f:
#     news_data = json.load(f)
#
# process_news_json(news_data)


import os
import re
import json
from dotenv import load_dotenv
from py2neo import Graph, Node, Relationship
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from neo4j import GraphDatabase


device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# Load environment variables
load_status = load_dotenv('.env')
if load_status is False:
    raise RuntimeError('Environment variables not loaded.')

# Neo4j config
URI = os.getenv('NEO4J_URI')
AUTH = (os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))

# Verify connectivity
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection to Neo4j established.")

# Also create a py2neo Graph object
graph = Graph(URI, auth=AUTH)

# Set up LLM model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3.5-mini-instruct", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3.5-mini-instruct", trust_remote_code=True).to(device)


def extract_json_blocks(text):
    """
    Returns a list of all top-level {...} blocks
    (non-greedy: first '{' up to matching '}', repeated).
    This won't handle deeply nested objects perfectly,
    but often is enough if the model returns separate blocks.
    """
    pattern = r'\{(?:[^{}]|(\{[^{}]*\}))*\}'
    # Or more simply: r'\{[^}]*\}' if you expect minimal nesting
    # but that can break on deeper nested braces.

    return re.findall(pattern, text, flags=re.DOTALL)

def generate_response(prompt):
    """
    Sends a prompt to the LLM and returns parsed JSON.
    """
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=500)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # If the model includes a '### Answer' separator, strip everything before it
    answer_match = re.search(r'### Answer\s*', response)
    if answer_match:
        response = response[answer_match.end():]

    # Search for a JSON object
    json_match = re.search(r'\{.*\}', response, re.DOTALL)

    blocks = extract_json_blocks(response)
    if not blocks:
        raise ValueError("No JSON found.")

    # Usually you only need the LAST or the FIRST valid block
    raw_json = blocks[-1]  # pick the last block
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse final JSON block: {e}")

    # if json_match:
    #     raw_json = json_match.group(0)
    #     try:
    #         # If the model returns placeholders like { ... }, remove them
    #         sanitized_json = re.sub(r'\{\s*\.\.\.\s*\}', '{}', raw_json).strip()
    #         return json.loads(sanitized_json)
    #     except json.JSONDecodeError as e:
    #         print(f"Failed to parse JSON. Raw output:\n{raw_json}\nError: {e}")
    #         raise ValueError("Invalid JSON format returned by LLM.")
    # else:
    #     raise ValueError("No valid JSON found in LLM response.")


def extract_entities_relationships(article):
    """
    Sends the article content to the LLM, requesting a JSON structure with
    { entities: { people: [], organizations: [], events: [] }, relationships: [] }.
    """
    # Safely retrieve fields
    title = article.get('title', 'Unknown title')
    source_name = article.get('source', {}).get('name', 'Unknown source')
    author = article.get('author', 'Unknown author')
    published_at = article.get('publishedAt', 'Unknown date')
    content = article.get('content', '')

    prompt = f"""
You are an IT and database expert who extracts structured knowledge from news articles.
The article below has a title, source, author, published date, and content. 
Please extract the following:
- Entities (people, organizations, events)
- Relationships among these entities

**Return ONLY valid JSON** in this exact structure (no extra text!):

{{
  "entities": {{
    "people": ["Alice", "Bob"],
    "organizations": ["UN", "ACME Corp"],
    "events": ["MajorElection"]
  }},
  "relationships": [
    {{
      "source": "Rwanda",
      "relation": "supports",
      "target": "M23 rebels"
    }}
  ]
}}

----------------
Article:
Title: "{title}"
Source: "{source_name}"
Author: "{author}"
Published At: "{published_at}"
Content: "{content}"
----------------
    """

    structured_data = generate_response(prompt)
    print("LLM JSON output:", structured_data)

    # structured_data is already a Python dictionary, so just return it
    return structured_data


def store_in_neo4j(structured_data):
    """
    Expects structured_data in the form:
    {
        "entities": {
            "people": [...],
            "organizations": [...],
            "events": [...]
        },
        "relationships": [
            {
                "source": "...",
                "relation": "...",
                "target": "..."
            }
        ]
    }
    """
    data = structured_data

    # Safely extract the lists. If keys are missing, default to empty list.
    people = data.get("entities", {}).get("people", [])
    orgs = data.get("entities", {}).get("organizations", [])
    events = data.get("entities", {}).get("events", [])
    relationships = data.get("relationships", [])

    # Merge/Upsert People
    for person_name in people:
        person_node = Node("Person", name=person_name)
        graph.merge(person_node, "Person", "name")

    # Merge/Upsert Organizations
    for org_name in orgs:
        org_node = Node("Organization", name=org_name)
        graph.merge(org_node, "Organization", "name")

    # Merge/Upsert Events
    for event_name in events:
        event_node = Node("Event", name=event_name)
        graph.merge(event_node, "Event", "name")

    # Create Relationships
    for relation in relationships:
        source_name = relation.get("source")
        rel_type = relation.get("relation")
        target_name = relation.get("target")

        if not (source_name and rel_type and target_name):
            # skip malformed relationships
            continue

        source_node = graph.nodes.match(name=source_name).first()
        target_node = graph.nodes.match(name=target_name).first()

        if source_node and target_node:
            rel = Relationship(source_node, rel_type.upper(), target_node)
            graph.merge(rel)


def process_news_json(news_json):
    """
    Takes a JSON object containing multiple articles, processes each one with an LLM,
    and stores structured knowledge in Neo4j.
    """
    articles = news_json.get("articles", [])

    for article in articles:
        try:
            structured_data = extract_entities_relationships(article)  # LLM processes article
            store_in_neo4j(structured_data)  # Store processed data in Neo4j
        except Exception as e:
            print(f"Error processing article: {article.get('title', 'No Title')}\n{e}")

    return {"status": "Knowledge graph updated"}


if __name__ == "__main__":
    with open("../KG-Builder/political_news_20250217_164112.json", "r", encoding="utf-8") as f:
        news_data = json.load(f)

    result = process_news_json(news_data)
    print(result)
