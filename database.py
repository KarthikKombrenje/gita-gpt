# database.py
"""Database connection and session management for SQLAlchemy and MongoDB."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient
from config import MYSQL_DATABASE_URL
engine = create_engine(MYSQL_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


client = MongoClient("mongodb://localhost:27017")
db = client.gita_gpt_db
chat_collection = db.chats
