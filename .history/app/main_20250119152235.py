from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from .services.weather_service import WeatherService
from .utils.database import get_db, init_db
from .models.database import WeatherRecord, School, NetworkOutage
from pydantic import BaseModel
from .services.prediction_service import PredictionService
from .services.alert_service import AlertService

app = FastAPI(title="Network Outage Forecaster")
weather_service = WeatherService()
prediction_service = PredictionService()

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

@app.get("/predict/{school_id}")
async def predict_outage(school_id: int, db: Session = Depends(get_db)):
    """Predict outage risk for a specific school"""
    # Get school
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Get current weather
    weather_data = await weather_service.get_current_weather(
        school.latitude,
        school.longitude
    )
    if not weather_data:
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")
    
    # Train model if not trained
    if not prediction_service.is_trained:
        if not prediction_service.train_model(db):
            return {
                "warning": "Not enough historical data for accurate predictions",
                "recommendation": "Continue collecting weather and outage data"
            }
    
    # Get prediction
    prediction = prediction_service.predict_outage_risk(weather_data)
    
    return {
        "school_name": school.name,
        "current_weather": weather_data,
        "prediction": prediction
    }

@app.get("/predictions/retrain")
async def retrain_model(db: Session = Depends(get_db)):
    """Force model retraining"""
    success = prediction_service.train_model(db)
    return {
        "success": success,
        "message": "Model retrained successfully" if success else "Not enough data for training"
    }

@app.get("/predict/{school_id}/with-alerts")
async def predict_and_alert(school_id: int, db: Session = Depends(get_db)):
    """Predict outage risk and send alerts if necessary"""
    # Get school
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Get current weather
    weather_data = await weather_service.get_current_weather(
        school.latitude,
        school.longitude
    )
    if not weather_data:
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")
    
    # Get prediction
    if not prediction_service.is_trained:
        prediction_service.train_model(db)
    
    prediction = prediction_service.predict_outage_risk(weather_data)
    prediction['current_weather'] = weather_data
    
    # Send alerts if risk is high enough
    alert_results = await alert_service.send_alerts(
        school.name,
        school.contact_email,
        school.contact_phone,
        prediction
    )
    
    return {
        "school_name": school.name,
        "prediction": prediction,
        "alerts_sent": alert_results
    }

@app.post("/alerts/test/{school_id}")
async def test_alerts(school_id: int, db: Session = Depends(get_db)):
    """Test the alert system for a specific school"""
    school = db.query(School).filter(School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Create test risk data
    test_risk_data = {
        "risk_score": 0.8,
        "message": "TEST ALERT - High risk of network outage",
        "current_weather": {
            "temperature": 25,
            "humidity": 80,
            "wind_speed": 15
        }
    }
    
    # Send test alerts
    alert_results = await alert_service.send_alerts(
        school.name,
        school.contact_email,
        school.contact_phone,
        test_risk_data
    )
    
    return {
        "message": "Test alerts triggered",
        "results": alert_results
    }