# This will test the environment to ensure that the .env file is set up
# correctly and that the OpenAI and Neo4j connections are working.
import os
import unittest
from dotenv import load_dotenv, find_dotenv
import torch
from neo4j import GraphDatabase
from py2neo import Graph

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