"""Contains utility functions for extracting text from PDFs and splitting text into chunks."""
import io
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
from log_config import logger


nltk.download('punkt')


# SECRET_KEY = "your_secret_key"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def extract_text_from_pdf(pdf_path):
#     """Extracts text from a PDF file."""
#     text = ""
#     with open(pdf_path, "rb") as file:
#         reader = PyPDF2.PdfReader(file)
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text

# def split_text(text, chunk_size=1000, chunk_overlap=100):
#     """Splits text into smaller chunks with specified size and overlap."""
#     chunks = []
#     start = 0
#     while start < len(text):
#         end = start + chunk_size
#         chunks.append(text[start:end])
#         start = end - chunk_overlap
#     return chunks

# def split_text_by_paragraph_and_sentence(text, chunk_size=5000, chunk_overlap=500):
#     """Splits text into smaller chunks based on paragraphs and sentences."""
#     paragraphs = text.split('\n\n')
#     chunks = []
#     current_chunk = ""
#     seperators = "\n\n"
#     tokenizer = tiktoken.get_encoding("cl100k_base")
#     for para in paragraphs:
#         para = para.strip()
#         if not para:
#             continue
#         # If para + current_chunk + seperators fits then add it to current chunk
#         if len(current_chunk) + len(para) +len(seperators) <= chunk_size:
#             current_chunk += para + seperators
#             logger.info("")  # Placeholder for debugging
#             logger.info("")
#             # Paragraph too big? check if current_chunk is not empty ,
#               append current_chunk to chunks
#             if len(para) > chunk_size :
#                 if current_chunk:
#                     chunks.append(current_chunk.strip())
#                     current_chunk = ""

#                 # Split large paragraph into sentences
#                 logger.info(f"para has tokens : {len(tokenizer.encode(para))}")
#                 sentences = sent_tokenize(para)

#                 temp_chunk = ""
#                 for sent in sentences:
#                     if len(temp_chunk) + len(sent) <= chunk_size:
#                         temp_chunk += sent + " "
#                     else:
#                         # Overlap the last 100 characters of temp_chunk
#                         # Overlap the last 100 characters of temp_chunk
#                         # only if temp_chunk > 100
#                         overlap_text = (
#                          temp_chunk[-chunk_overlap:]
#                          if chunk_overlap < len(temp_chunk)
#                          else temp_chunk
#             )
#                         temp_chunk = overlap_text + sent + " "
#                 if temp_chunk:
#                     chunks.append(temp_chunk.strip())
#             else:
#                 # Add current chunk to list and start new chunk with this paragraph
#                 if current_chunk:
#                     chunks.append(current_chunk.strip())
#                 current_chunk = para + "\n\n"
#     if current_chunk:
#         chunks.append(current_chunk.strip())
#     return chunks

def split_text_by_sentence(text, chunk_size=6000, chunk_overlap=600):
    """Splits text into smaller chunks based on sentences."""
    sentences = sent_tokenize(text)
    chunks = []
    for sentence in sentences:
        sentence = sentence.strip()
        logger.info("sentence has size: %s ", len(sentence))

        if len(sentence) + 1 <= chunk_size:
            chunks.append(sentence + " ")
            logger.info("chunk length : %s ", len(chunks))
        else:
            # Recursively split large sentence
            start = 0
            while start < len(sentence):
                end = start + chunk_size
                if end < len(sentence):
                    chunks.append(sentence[start:end])
                    start = end - chunk_overlap
                else:
                    chunks.append(sentence[start:])
                    break
    logger.info("Total chunks: %s ", len(chunks))
    return chunks


def extract_text_from_bytes(file_bytes: bytes) -> str:
    """Extracts text from PDF bytes."""
    text = ""
    file_stream = io.BytesIO(file_bytes)
    reader = PyPDF2.PdfReader(file_stream)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text
