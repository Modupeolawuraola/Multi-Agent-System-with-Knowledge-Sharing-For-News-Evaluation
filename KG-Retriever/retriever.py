
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
from langchain_neo4j import Neo4jGraph, Neo4jVector


from dotenv import load_dotenv
import boto3
import os
load_dotenv()

def create_bedrock_client():
    """Create bedrock authenticated Bedrock client"""
    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        bedrock_client= session.client(service_name='bedrock-runtime',
                                       region_name=os.getenv('AWS_REGION', 'us-east-1')
                                       )
        return bedrock_client
    except Exception as e:
        print(f"Error creating bedrock client: {e}")
        raise

def create_llm():
    """Create Bedrock LLm Instance"""
    try:
        client = create_bedrock_client()
        #initialize anthropic calude model through bedrock

        llm= ChatBedrock(
            client= client,
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0",
            model_kwargs={
                "max_tokens":4096,
                "temperature":0.2,
                "top_p":0.9
            }
        )
        return llm
    except Exception as e:
        print(f"Error initializing Bedrock LLM: {e}")
        raise
def create_embedder():
    """Create Bedrock LLm Instance"""
    try:
        client = create_bedrock_client()
        #initialize anthropic calude model through bedrock

        embedder = ChatBedrock(
            client= client,
            model_id = "amazon.titan-embed-text-v2:0",
        )
        return embedder
    except Exception as e:
        print(f"Error initializing Bedrock Embedder: {e}")
        raise

llm = create_llm()
embedder = create_embedder()

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

chunk_vector = Neo4jVector.from_existing_index(
    embedder,
    graph=graph,
    index_name="chunkVector",
    embedding_node_property="textEmbedding",
    text_node_property="text",
    retrieval_query="""
// get the document
MATCH (node)-[:PART_OF]->(d:Document)
WITH node, score, d

// get the entities and relationships for the document
MATCH (node)-[:HAS_ENTITY]->(e)
MATCH p = (e)-[r]-(e2)
WHERE (node)-[:HAS_ENTITY]->(e2)

// unwind the path, create a string of the entities and relationships
UNWIND relationships(p) as rels
WITH 
    node, 
    score, 
    d, 
    collect(apoc.text.join(
        [labels(startNode(rels))[0], startNode(rels).id, type(rels), labels(endNode(rels))[0], endNode(rels).id]
        ," ")) as kg
RETURN
    node.text as text, score,
    { 
        document: d.id,
        entities: kg
    } AS metadata
"""
)

instructions = (
    "Use the given context to answer the question."
    "Reply with an answer that includes the id of the document and other relevant information from the text."
    "If you don't know the answer, say you don't know."
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)

chunk_retriever = chunk_vector.as_retriever()
chunk_chain = create_stuff_documents_chain(llm, prompt)
chunk_retriever = create_retrieval_chain(
    chunk_retriever,
    chunk_chain
)

def find_chunk(q):
    return chunk_retriever.invoke({"input": q})

while (q := input("> ")) != "exit":
    print(find_chunk(q))