import bcrypt
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models


app = FastAPI()

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

db = SessionLocal()
@app.post('/register', status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate):
    db_user = db.query(models.User).filter(models.User.username == user_create.username).first()

    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    hashed_password = hash_password(user_create.password)
    new_user = models.User(username=user_create.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    statement = str(new_user.username)
    return statement +  ' created'

@app.post('/login', response_model=User)
def login_user(user_create: UserCreate):
    db_user = db.query(models.User).filter(models.User.username == user_create.username).first()

    if db_user is None or not verify_password(user_create.password ,db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    print(db_user.username)
    print(db_user.password)
    print(verify_password(user_create.password,db_user.password))

    return User(username=db_user.username)
