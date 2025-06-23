import sqlite3
from pathlib import Path
import uuid
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi import security
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError
import jwt
from pathlib import Path
import sqlite3
import os


from auth import ALGO, SECRET

def init_db():
    # Resolve correct path (use absolute path with home directory)
    base_path = Path.home() / "OneDrive" / "Desktop" / "minor projects" / "enterprise-chat"
    db_path = base_path / "shared" / "chat.db"
    
    # Create directory if missing
    os.makedirs(db_path.parent, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT
        )
    ''')
    #audit_log table [5][9]
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        user TEXT,
        action TEXT,
        details TEXT
    )
    ''')
    # Create audit triggers [5][9]
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS messages_audit_insert
        AFTER INSERT ON messages
        BEGIN
            INSERT INTO audit_log (user, action, details)
            VALUES (NEW.sender, 'INSERT', 'Created message: ' || NEW.id);
        END;
    ''')
    
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS messages_audit_update
        AFTER UPDATE ON messages
        BEGIN
            INSERT INTO audit_log (user, action, details)
            VALUES (NEW.sender, 'UPDATE', 'Modified message: ' || NEW.id);
        END;
    ''')
    
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS messages_audit_delete
        AFTER DELETE ON messages
        BEGIN
            INSERT INTO audit_log (user, action, details)
            VALUES (OLD.sender, 'DELETE', 'Deleted message: ' || OLD.id);
        END;
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS revoked_tokens (
        jti TEXT PRIMARY KEY,
        revoked_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def add_message(sender, message):
    conn = sqlite3.connect(Path(__file__).parents[1]/"shared/chat.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", (sender, message))
    conn.commit()
    conn.close()

def get_messages():
    conn = sqlite3.connect(Path(__file__).parents[1]/"shared/chat.db")
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM messages")
    messages = [{"sender": row[0], "message": row[1]} for row in cursor.fetchall()]
    conn.close()
    return messages

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