from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal,engine
from fastapi.middleware.cors import CORSMiddleware
import models

app = FastAPI()

origins = [
    "http://localhost:*",
    "http://localhost:5173",
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
models.Base.metadata.create_all(bind=engine)


class UserBase(BaseModel):
    username: str
    score: int

class UserModel(UserBase):
    pass
    class Config:
        orm_mode = True

class GameStatusBase(BaseModel):
    username: str
    status: str


@app.get('/')
async def read_root():
    return {'hello':'world'}

@app.get('/scores')
async def get_top_users(db: Session = Depends(get_db)):
    top_users = db.query(models.User).order_by(models.User.score.desc()).limit(10).all()
    return top_users

def player_exists(player_username:str,db:Session):

    exist = db.query(models.User).filter(models.User.username==player_username).first()

    if exist:
        return True
    return False


def commit_results_player(player_status:GameStatusBase,db:Session):

    exists = db.query(models.User).filter(models.User.username==player_status.username).first()

    if exists:
        player = exists
        if player_status.status=='WIN':
            player.score += 1
        elif player_status.status=='LOSE':
            player.score -= 1
        else:
            return False
        
        db.commit()
        db.refresh(player)
        return True
    
    else:
        player_username = player_status.username
        player_score = 0
        if player_status.status=='WIN':
            player_score = 1
        elif player_status.status=='LOSE':
            player_score = -1
        elif player_status.status=='DRAW':
            pass
        else:
            return False
        
        new_user = models.User(username = player_username, score = player_score)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return True


@app.post('/play',response_model=bool)
async def commit_result(Status: list[GameStatusBase], db: Session = Depends(get_db)):

    player1 = Status[0]
    player2 = Status[1]

    p1_result = commit_results_player(player1,db)
    p2_result = commit_results_player(player2,db)

    if p1_result and p2_result:
        return True
    return False
