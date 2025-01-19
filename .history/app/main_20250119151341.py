from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from .services.weather_service import WeatherService
from .utils.database import get_db, init_db
from .models.database import WeatherRecord, School, NetworkOutage
from pydantic import BaseModel
from .services.prediction_service import PredictionService

app = FastAPI(title="Network Outage Forecaster")
weather_service = WeatherService()

class SchoolCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    contact_email: str
    contact_phone: str

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/schools/")
async def create_school(school: SchoolCreate, db: Session = Depends(get_db)):
    db_school = School(**school.dict())
    db.add(db_school)
    db.commit()
    db.refresh(db_school)
    return db_school

@app.get("/schools/")
async def list_schools(db: Session = Depends(get_db)):
    schools = db.query(School).all()
    return schools

@app.get("/weather/{lat}/{lon}")
async def get_weather(lat: float, lon: float, db: Session = Depends(get_db)):
    weather_data = await weather_service.get_current_weather(lat, lon)
    if weather_data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")
    
    # Store weather data in database
    weather_record = WeatherRecord(
        latitude=lat,
        longitude=lon,
        **{k: v for k, v in weather_data.items() if k != 'timestamp'}
    )
    db.add(weather_record)
    db.commit()
    
    return weather_data

@app.post("/outages/report/{school_id}")
async def report_outage(school_id: int, db: Session = Depends(get_db)):
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    outage = NetworkOutage(school_id=school_id)
    db.add(outage)
    db.commit()
    db.refresh(outage)
    return outage