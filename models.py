from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    status_code: int
class ChatErrorResponse(BaseModel):
    question: str
    error: str
    status_code: int

class EmbedRequest(BaseModel):
    pdf_files: List[str]

class EmbedResponse(BaseModel):
    message: str