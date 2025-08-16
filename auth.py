"""
auth.py
--------
This module handles user authentication, including JWT token generation
and validation for API requests.
"""
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException,status
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
class TokenData(BaseModel):
    """Token data model for user authentication"""
    username: str

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Function to get the current user from the token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception from exc

def get_password_hash(password):
    """ Encode the password using bcrypt hashing. """
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    """ Verify the provided password against the hashed password. """
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta=None):
    """ Generate a JWT access token with an expiration time. """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
