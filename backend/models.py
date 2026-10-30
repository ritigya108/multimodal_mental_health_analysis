"""
SQLAlchemy ORM models.

Note: this project uses in-memory data structures for most state to avoid
requiring a database server in demo mode. These model definitions are kept
for completeness and future persistence work.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    age = Column(Integer, nullable=True)
    emergency_contact = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    journal_entries = relationship("JournalEntry", back_populates="user")
    risk_assessments = relationship("RiskAssessment", back_populates="user")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    content = Column(Text)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String, nullable=True)
    analyzed = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="journal_entries")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    risk_level = Column(String)
    risk_score = Column(Float)
    factors = Column(Text)
    recommendations = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="risk_assessments")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    message = Column(Text)
    response = Column(Text)
    sentiment = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
