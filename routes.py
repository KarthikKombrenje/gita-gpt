"""This file contains the FastAPI routes for user authentication, chat and PDF embedding."""
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pymongo import ReturnDocument
# Application-specific imports
from database import Base, engine, SessionLocal, chat_collection
from log_config import logger
import auth
import models
import schemas
from schemas import ChatMongoRequest, ChatQuestionResponse, ChatRequest, ChatResponse
from schemas import EmbedResponse, ChatErrorResponse, ShowChatsResponse
from service import chat_answer, embed_pdfs

router = APIRouter()

# Modern frameworks use FastAPI.
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Endpoint to register a new user."""
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
#Reloads the new_user object from the database.
#Ensures fields like id (auto-incremented primary key) are populated in Python memory.
#Makes new_user.id (and any other DB-generated fields) available immediately
    token = auth.create_access_token(data={"sub": new_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Endpoint to log in a user and return an access token."""
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def read_users_me(token_data=Depends(auth.get_current_user)):
    """Endpoint to get the current user's information."""
    return {"username": token_data.username}


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    req: ChatRequest,
    token_data = Depends(auth.get_current_user)
):
    """Endpoint to handle chat requests."""
    try:
        logger.info("Received chat request: '%s' from user: %s",req.question,token_data.username)
        answer = chat_answer(req.question)
        return ChatResponse(
            question=req.question,
            answer=answer,
            status_code=200
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        return JSONResponse(
            status_code=500,
            content=ChatErrorResponse(
                question=req.question,
                error=str(e),
                status_code=500
            ).dict()
        )

@router.post("/embed", response_model=EmbedResponse)
async def embed_endpoint(pdf_files: List[UploadFile] = File(...),
                    token_data = Depends(auth.get_current_user)):
    """Endpoint to handle PDF embedding requests."""
    logger.info("Embedding request: from user: %s",token_data.username)
    try:
        # Pass list of UploadFile objects to your service function
        await embed_pdfs(pdf_files)
        return EmbedResponse(message="PDFs successfully embedded.", status_code=200)
    except Exception as e:  # pylint: disable=broad-exception-caught
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/saveChats")
def save_chat(chat: ChatMongoRequest, token_data=Depends(auth.get_current_user)):
    """Endpoint to save or update a chat in MongoDB."""
    result = chat_collection.find_one_and_update(
        {
            "chat_name": chat.chat_name,
            "username": token_data.username  #  ensure it's tied to the logged-in user
        },
        {
            "$setOnInsert": {
                "chat_name": chat.chat_name,
                "username": token_data.username  #  ensure it's stored
            },
            "$push": {
                "question": chat.question,
                "answer": chat.answer,
            }
        },
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    return {"message": "Chat saved or updated", "id": str(result["_id"])}


@router.post("/showAllQuestions", response_model=ChatQuestionResponse)
def get_all_questions(token_data=Depends(auth.get_current_user)):
    """Endpoint to fetch all chat questions for the logged-in user."""
    # Filter only the logged-in user's chats
    logger.info("Fetching all questions for user: %s",{token_data.username})
    docs = chat_collection.find(
        {"username": token_data.username},  #  Filter condition
        {"_id": 0, "chat_name": 1}         #  Projection
    )

    all_questions = []
    for doc in docs:
        name = doc.get("chat_name")
        if name:
            all_questions.append(name)

    return {"question": all_questions}


@router.post("/findChatByName", response_model=ShowChatsResponse)
def find_chat_by_name(
    request: schemas.ChatNameRequest,
    token_data=Depends(auth.get_current_user)
):
    """Endpoint to find a chat by its name."""
    doc = chat_collection.find_one({"username": token_data.username,"chat_name": request.chat_name})

    if not doc:
        raise HTTPException(status_code=404, detail="No chat found with that chat_name.")

    questions = doc.get("question", [])
    answers = doc.get("answer", [])

    # Pair up Q&A into ChatMongoRequest list
    paired_chats = []
    for q, a in zip(questions, answers):
        paired_chats.append(ChatMongoRequest(
            chat_name=doc["chat_name"],
            question=q,
            answer=a
        ))

    return {"chats": paired_chats}
