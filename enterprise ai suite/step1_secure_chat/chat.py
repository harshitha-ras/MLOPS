from database import SessionLocal, Message
from datetime import datetime

def send_message(sender, receiver, content):
    db = SessionLocal()
    msg = Message(sender=sender, receiver=receiver, content=content, timestamp=datetime.utcnow())
    db.add(msg)
    db.commit()

def get_messages_for_user(username):
    db = SessionLocal()
    return db.query(Message).filter(Message.receiver == username).order_by(Message.timestamp.desc()).all()
