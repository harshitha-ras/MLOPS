from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth import get_current_user, create_access_token
from db import init_db, add_message, get_messages
from pydantic import BaseModel
from typing import List
import uvicorn
import bcrypt
from db import revoke_token
from pathlib import Path

print(Path(__file__).parents[1]/"shared/chat.db")

app = FastAPI()

origins = ["*"]  # Allow all for local use

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserLogin(BaseModel):
    username: str
    password: str

class ChatMessage(BaseModel):
    sender: str
    message: str

@app.post("/login")
def login(user: UserLogin):
    # Hardcoded for demo (replace with DB lookup)
    stored_hash = bcrypt.hashpw(b"admin", bcrypt.gensalt()) 
    
    if user.username == "admin" and bcrypt.checkpw(user.password.encode(), stored_hash):
        return {"access_token": create_access_token(user.username)}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/messages", response_model=List[ChatMessage])
def fetch_messages(user=Depends(get_current_user)):
    return get_messages()

@app.post("/send")
def send_message(msg: ChatMessage, user=Depends(get_current_user)):
    add_message(msg.sender, msg.message)
    return {"reply": f"Bot says: Hello {msg.sender}, you said '{msg.message}'"}

@app.post("/logout")
def logout(user=Depends(get_current_user)):
    # In real implementation, get jti from token
    revoke_token("current_token_jti")  
    return {"detail": "Successfully logged out"}


if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)