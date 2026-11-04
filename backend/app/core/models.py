from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, default="Madi Trader")
    created_at = Column(DateTime, default=utc_now)

class Instrument(Base):
    __tablename__ = "instruments"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, default="FOREX_MAJOR")
    pip_size = Column(Float, default=0.0001)
    digits = Column(Integer, default=5)
    margin_rate = Column(Float, default=0.01)

class Workspace(Base):
    __tablename__ = "chart_workspaces"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, default="Default Workspace")
    layout = Column(String, default="single")
    config_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    target_price = Column(Float, nullable=False)
    condition = Column(String, default="ABOVE")
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

class PaperAccount(Base):
    __tablename__ = "paper_accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    currency = Column(String, default="USD")
    balance = Column(Float, default=100000.0)
    equity = Column(Float, default=100000.0)
    margin_used = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)
