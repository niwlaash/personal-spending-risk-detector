"""
Database models and connection setup using SQLAlchemy.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Transaction(Base):
    """Represents a single financial transaction."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    balance = Column(Float, nullable=True)
    category = Column(String(100), nullable=True)
    source_bank = Column(String(100), nullable=True, default="unknown")
    upload_batch = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskReport(Base):
    """Stores computed risk reports."""

    __tablename__ = "risk_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    financial_risk_score = Column(Float, nullable=False)
    burnout_risk_score = Column(Float, nullable=False)
    financial_risk_level = Column(String(20), nullable=False)
    burnout_risk_level = Column(String(20), nullable=False)
    insights = Column(Text, nullable=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI: yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
