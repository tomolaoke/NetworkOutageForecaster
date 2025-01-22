from sqlalchemy import (
    create_engine, Column, Integer, Float,
    String, DateTime, Boolean, ForeignKey)
from sqlalchemy.orm import relationship
from datetime import datetime
from fastapi_users import models
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from . import TimestampedModel


class WeatherRecord(TimestampedModel):
    __tablename__ = "weather_records"
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float)
    longitude = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    weather_condition = Column(String)
    weather_description = Column(String)
    rain_last_hour = Column(Float)
    clouds = Column(Integer)
    cloud = Column(Integer)


class School(TimestampedModel):
    __tablename__ = "schools"
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    contact_email = Column(String)
    contact_phone = Column(String)


class NetworkOutage(TimestampedModel):
    __tablename__ = "network_outages"
    school_id = Column(Integer, ForeignKey('schools.id'))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    cause = Column(String, nullable=True)
    school = relationship("School", backref="outages")


class User(TimestampedModel, SQLAlchemyBaseUserTableUUID):
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)


