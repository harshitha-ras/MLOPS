from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from pydantic_settings import BaseSettings
import uuid
import sqlite3
from pathlib import Path

class SecuritySettings(BaseSettings):
    jwt_secret: str = "default_secret"
    jwt_algo: str = "HS256"
    db_path: str = Path(__file__).parents[1]/"shared/chat.db"  # Add this field

    class Config:
        env_file = ".env"

settings = SecuritySettings()
SECRET = settings.jwt_secret
ALGO = settings.jwt_algo

security = HTTPBearer()

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode({"sub": username, "exp": expire}, SECRET, algorithm=ALGO)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

def revoke_token(jti: str):
    conn = sqlite3.connect(Path(__file__).parents[1]/"shared/chat.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO revoked_tokens (jti) VALUES (?)", (jti,))
    conn.commit()
    conn.close()

def is_token_revoked(jti: str) -> bool:
    conn = sqlite3.connect(Path(__file__).parents[1]/"shared/chat.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM revoked_tokens WHERE jti = ?", (jti,))
    return cursor.fetchone()[0] > 0

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=1)
    jti = str(uuid.uuid4())
    return jwt.encode({"sub": username, "exp": expire, "jti": jti}, SECRET, algorithm=ALGO)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        if is_token_revoked(payload['jti']):  # Check revocation
            raise HTTPException(status_code=403, detail="Revoked token")
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")