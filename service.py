"""Contains the main service logic for embedding PDFs and answering questions using Chat API."""
import random
import time
from typing import List

import tiktoken
from dotenv import load_dotenv
from openai import APIConnectionError, APIError, OpenAI, RateLimitError
from fastapi import UploadFile

from repo import upsert_documents, query_documents
from utils import extract_text_from_bytes, split_text_by_sentence
from log_config import logger

load_dotenv()

# Keep names uppercase to satisfy naming style
OPENAI_CLIENT = OpenAI(timeout=30.0, max_retries=5)


async def embed_pdfs(pdf_files: List[UploadFile]):
    """Process a list of PDF files, extract text, split into chunks, embed, and upsert."""
    chunked_documents = []

    for upload_file in pdf_files:
        logger.info("Processing PDF: %s", upload_file.filename)

        # Read bytes from UploadFile asynchronously
        file_bytes = await upload_file.read()

        # Extract text and chunk
        full_text = extract_text_from_bytes(file_bytes)
        chunks = split_text_by_sentence(full_text)

        tokenizer = tiktoken.get_encoding("cl100k_base")
        for i, chunk in enumerate(chunks):
            tokens_in_chunk = len(tokenizer.encode(chunk))
            logger.info("Chunk %s has %s tokens", i + 1, tokens_in_chunk)

        logger.info("Extracted text into %s chunks for %s", len(chunks), upload_file.filename)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{upload_file.filename}_chunk{i+1}"
            logger.info("Preparing chunk %s with id: %s", i + 1, chunk_id)
            chunked_documents.append({"id": chunk_id, "text": chunk})

    logger.info("Total chunks to embed: %s", len(chunked_documents))

    # Generate embeddings and upsert to Chroma
    for i, doc in enumerate(chunked_documents):
        logger.info("Embedding chunk %s/%s: %s", i + 1, len(chunked_documents), doc["id"])
        for attempt in range(5):
            try:
                # Create embedding for the text chunk
                embedding = (
                    OPENAI_CLIENT.embeddings.create(
                        input=doc["text"],
                        model="text-embedding-3-small",
                    ).data[0].embedding
                )

                # Upsert (wrap to keep line length tidy)
                upsert_documents(
                    ids=[doc["id"]],
                    documents=[doc["text"]],
                    embeddings=[embedding],
                )

                logger.info("Upserted chunk %s/%s: %s", i + 1, len(chunked_documents), doc["id"])
                break
            except (APIError, RateLimitError, APIConnectionError, TimeoutError) as exc:
                # Exponential backoff
                logger.info(
                    "Retry %s/5 for chunk %s in %.1fs due to error: %s",
                    attempt + 1,
                    doc["id"],
                    2 ** attempt + random.random(),
                    exc,
                )
                time.sleep(2 ** attempt + random.random())

    logger.info("Finished embedding all PDF chunks")


def load_prompt_template() -> str:
    """Loads the prompt template from a text file for generating responses."""
    with open("prompts/mentor_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


PROMPT_TEMPLATE = load_prompt_template()


def chat_answer(question: str) -> str:
    """Generates a chat response based on the question and context from the embedded documents."""
    chunks = query_documents(question)
    context = "\n\n".join(chunks)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    logger.info("Prompt is ------- %s", prompt)

    response = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content
