from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    title = Column(String(100))
    contact = Column(String(20))

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    section = Column(String(50))  # 'topics', 'profiles', etc.
    topic_key = Column(String(50))  # e.g., 'collab', 'career'
    content = Column(Text, nullable=False)
    dtcreated = Column(DateTime, default=datetime.utcnow)

class TopicUnread(Base):
    __tablename__ = 'topic_unreads'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic_key = Column(String(50), nullable=False)
    unread_count = Column(Integer, default=0)
