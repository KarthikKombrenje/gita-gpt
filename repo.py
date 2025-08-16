"""Module for managing the ChromaDB collection for Bhagavad Gita documents."""

import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_EF = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY, model_name="text-embedding-3-small"
)

CHROMA_CLIENT = chromadb.PersistentClient(path="chroma_persistent_storage")
COLLECTION = CHROMA_CLIENT.get_or_create_collection(
    name="gita_pdf_collection", embedding_function=OPENAI_EF

)

def upsert_documents(ids, documents, embeddings):
    """Upserts documents into the ChromaDB collection."""
    COLLECTION.upsert(ids=ids, documents=documents, embeddings=embeddings)

def query_documents(question, n_results=10):
    """Queries the ChromaDB collection for documents related to the question."""
    results = COLLECTION.query(query_texts=[question], n_results=n_results)
    return [doc for sublist in results["documents"] for doc in sublist]
