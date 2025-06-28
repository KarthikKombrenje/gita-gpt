import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_key, model_name="text-embedding-3-small"
)

chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection = chroma_client.get_or_create_collection(
    name="gita_pdf_collection", embedding_function=openai_ef
)

def upsert_documents(ids, documents, embeddings):
    collection.upsert(ids=ids, documents=documents, embeddings=embeddings)

def query_documents(question, n_results=3):
    results = collection.query(query_texts=[question], n_results=n_results)
    return [doc for sublist in results["documents"] for doc in sublist]
