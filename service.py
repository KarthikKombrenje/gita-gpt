import os
from dotenv import load_dotenv
from openai import OpenAI
from repo import upsert_documents, query_documents
from fastapi import UploadFile
from typing import List
from utils import extract_text_from_bytes,split_text_by_sentence
import tiktoken
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

async def embed_pdfs(pdf_files: List[UploadFile]):
    chunked_documents = []
    for upload_file in pdf_files:
        print(f"Processing PDF: {upload_file.filename}")
        
        # Read bytes from UploadFile asynchronously , because we are uploading the pdf
        file_bytes = await upload_file.read()
        
        # Extract text from bytes (modify utils.py to accept bytes)
        full_text = extract_text_from_bytes(file_bytes)
        chunks = split_text_by_sentence(full_text)
        tokenizer = tiktoken.get_encoding("cl100k_base")
        
        
        for i, chunk in enumerate(chunks):
            tokens_in_chunk = len(tokenizer.encode(chunk))
            print("chunk ",i+1," has tokens ",tokens_in_chunk)
        print(f"Extracted text and split into {len(chunks)} chunks for {upload_file.filename}")
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{upload_file.filename}_chunk{i+1}"
            print(f"Preparing chunk {i+1} with id: {chunk_id}")
            chunked_documents.append({
                "id": chunk_id,
                "text": chunk
            })

    print(f"Total chunks to embed: {len(chunked_documents)}")

    # Generate embeddings and upsert to chroma 
    for i, doc in enumerate(chunked_documents):
        print(f"Embedding chunk {i+1}/{len(chunked_documents)}: {doc['id']}")
        embedding = client.embeddings.create(input=doc["text"], model="text-embedding-3-small").data[0].embedding
        upsert_documents(ids=[doc["id"]], documents=[doc["text"]], embeddings=[embedding])
        print(f"Upserted chunk {i+1}/{len(chunked_documents)}: {doc['id']}")

    print("Finished embedding all PDF")


def load_prompt_template() -> str:
    with open("prompts/mentor_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()

PROMPT_TEMPLATE = load_prompt_template()

def chat_answer(question: str) -> str:
    chunks = query_documents(question)
    context = "\n\n".join(chunks)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    print("prompt is -------",prompt)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
    )
    #return response
    return response.choices[0].message.content
