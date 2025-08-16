"""SQLAlchemy ORM models."""
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    """SQLAlchemy model for User."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(200))

    def __repr__(self) -> str:
        return f"<User(username={self.username})>"

    def to_dict(self) -> dict:
        """Convert User instance to dictionary."""
        return {"id": self.id, "username": self.username, "email": self.email}
