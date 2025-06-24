from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from database import SessionLocal, User
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "secret"
ALGORITHM = "HS256"

def hash_pw(password):
    return pwd_context.hash(password)

def verify_pw(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(username):
    payload = {"sub": username, "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
    except:
        return None

def register_user(username, password):
    db = SessionLocal()
    user = User(username=username, password=hash_pw(password))
    try:
        db.add(user)
        db.commit()
        return True
    except IntegrityError:
        return False

def authenticate_user(username, password):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if user and verify_pw(password, user.password):
        return create_token(user.username)
    return None
