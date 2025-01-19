from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# [Previous WeatherRecord, School, and NetworkOutage classes remain the same]

# app/utils/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.database import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./outageoracle.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from services.weather_service import WeatherService
from utils.database import get_db, init_db
from models.database import WeatherRecord, School, NetworkOutage
from pydantic import BaseModel