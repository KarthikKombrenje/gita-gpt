"""Entry point for the Bhagavad Gita Chat API using FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
#this launches the application like main() in java / springboot
app = FastAPI(title="Bhagavad Gita Chat API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")
