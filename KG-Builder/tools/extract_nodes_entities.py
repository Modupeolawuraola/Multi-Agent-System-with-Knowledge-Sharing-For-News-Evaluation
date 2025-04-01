import os
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.llms import HuggingFacePipeline
from langchain_experimental.graph_transformers import LLMGraphTransformer
import torch
import text_splitter

device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "phi-3.5-mini-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id).to(device)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=1024,
    temperature=0.7,
)

llm = HuggingFacePipeline(pipeline=pipe)

doc_transformer = LLMGraphTransformer(
    llm=llm,
    )
chunks = text_splitter.chunks

for chunk in chunks:
    # Generate the entities and relationships from the chunk
    graph_docs = doc_transformer.convert_to_graph_documents([chunk])