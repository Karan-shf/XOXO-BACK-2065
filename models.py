from database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "User"
    username =  Column(String,primary_key=True)
    score = Column(Integer)
