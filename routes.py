from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List

from fastapi.responses import JSONResponse
from models import ChatRequest, ChatResponse, EmbedRequest, EmbedResponse, ChatErrorResponse
from service import chat_answer, embed_pdfs

router = APIRouter()
# Modern frame works use fastapi .
@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        answer = chat_answer(req.question)
        return ChatResponse(question=req.question, answer=answer, status_code=200)
    except Exception as e:
            return JSONResponse(
            status_code=500,
            content=ChatErrorResponse(
                question=req.question,
                error=str(e),
                status_code=500
            ).dict()
            )

@router.post("/embed", response_model=EmbedResponse)
async def embed_endpoint(pdf_files: List[UploadFile] = File(...)):
    try:
        # Pass list of UploadFile objects to your service function 
        await embed_pdfs(pdf_files)
        return EmbedResponse(message="PDFs successfully embedded.",status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))