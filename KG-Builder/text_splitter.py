from langchain.text_splitter import CharacterTextSplitter
import load_data
docs = load_data.docs

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1500,
    chunk_overlap=200,
)

chunks = text_splitter.split_documents(docs)
print(chunks)