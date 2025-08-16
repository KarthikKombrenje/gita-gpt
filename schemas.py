"""Pydantic request/response schemas."""
from typing import List
from pydantic import BaseModel, EmailStr


# ---- Auth/User ----
class UserCreate(BaseModel):
    """Model for user registration."""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Model for user login."""
    username: str
    password: str


# If you had LoginRequest elsewhere, alias it to avoid duplication:
LoginRequest = UserLogin


class Token(BaseModel):
    """Model for access token response."""
    access_token: str
    token_type: str


class ChatNameRequest(BaseModel):
    """Model for chat name request."""
    chat_name: str


# ---- Chat ----
class ChatRequest(BaseModel):
    """Model for chat request containing the question."""
    question: str


class ChatMongoRequest(BaseModel):
    """Model for chat request with additional fields for chat name and answer."""
    chat_name: str
    question: str
    answer: str


class ChatResponse(BaseModel):
    """Model for chat response containing the question, answer, and status code."""
    question: str
    answer: str
    status_code: int


class ChatErrorResponse(BaseModel):
    """Model for error response in chat requests."""
    question: str
    error: str
    status_code: int

    def __repr__(self) -> str:
        return f"<ChatErrorResponse(error={self.error}, status_code={self.status_code})>"


# ---- Embedding/Uploads ----
class EmbedResponse(BaseModel):
    """Model for embedding response containing a success message and status code."""
    message: str
    status_code: int

class ShowChatsResponse(BaseModel):
    """Model for showing chats responses."""
    chats: List[ChatMongoRequest]


class ChatQuestionResponse(BaseModel):
    """Model for chat question list."""
    question: List[str]
