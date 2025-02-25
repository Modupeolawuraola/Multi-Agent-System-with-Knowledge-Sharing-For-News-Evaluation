import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jGraph
import text_splitter
from dotenv import load_dotenv
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
embedding_provider = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

load_status = load_dotenv('../.env')
if load_status is False:
    raise RuntimeError('Environment variables not loaded.')

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

chunks = text_splitter.chunks

for chunk in chunks:

    # Extract the filename
    filename = os.path.basename(chunk.metadata["source"])

    # Create a unique identifier for the chunk
    chunk_id = f"{filename}.{chunk.metadata["seq_num"]}"

    # Embed the chunk
    chunk_embedding = embedding_provider.embed_query(chunk.page_content)

    # Add the Document and Chunk nodes to the graph
    properties = {
        "filename": filename,
        "chunk_id": chunk_id,
        "text": chunk.page_content,
        "embedding": chunk_embedding
    }

    graph.query("""
        MERGE (d:Document {id: $filename})
        MERGE (c:Chunk {id: $chunk_id})
        SET c.text = $text
        MERGE (d)<-[:PART_OF]-(c)
        WITH c
        CALL db.create.setNodeVectorProperty(c, 'textEmbedding', $embedding)
        """,
        properties
    )

existing_indexes = graph.query("""
    SHOW INDEXES YIELD name
    WHERE name = 'vector'
    RETURN name
""")

# If the list is empty, the index doesn't exist; go ahead and create it.
if not existing_indexes:  # or check length etc.
    graph.query("""
        CREATE VECTOR INDEX `vector`
        FOR (c:Chunk) ON (c.embedding)
        OPTIONS {
            indexConfig: {
                `vector.dimensions`: 384,
                `vector.similarity_function`: 'cosine'
            }
        };
    """)