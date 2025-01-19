import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.database import WeatherRecord, NetworkOutage, School

class PredictionService:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self, weather_data):
        """Convert weather data into ML features"""
        features = [
            'temperature', 'humidity', 'wind_speed',
            'rain_last_hour', 'clouds'
        ]
        
        return np.array([
            weather_data.get(f, 0) for f in features
        ]).reshape(1, -1)

    def train_model(self, db: Session):
        """Train the model using historical data"""
        # Get historical data
        weather_records = db.query(WeatherRecord).all()
        outages = db.query(NetworkOutage).all()
        
        if not weather_records or not outages:
            return False
        
        # Prepare training data
        X = []
        y = []
        
        for weather in weather_records:
            # Create feature vector
            features = [
                weather.temperature,
                weather.humidity,
                weather.wind_speed,
                weather.rain_last_hour,
                weather.clouds
            ]
            
            # Check if there was an outage within 6 hours of this weather record
            outage_occurred = any(
                abs((outage.start_time - weather.timestamp).total_seconds()) <= 21600
                for outage in outages
            )
            
            X.append(features)
            y.append(1 if outage_occurred else 0)
        
        if len(X) < 10:  # Need minimum amount of data
            return False
        
        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X, y)
        self.is_trained = True
        return True

    def predict_outage_risk(self, weather_data: dict) -> dict:
        """Predict the risk of an outage based on weather conditions"""
        if not self.is_trained:
            return {
                "risk_score": 0.5,  # Default medium risk
                "confidence": 0.0,
                "message": "Model not yet trained - insufficient data"
            }
        
        # Prepare features
        features = self.prepare_features(weather_data)
        features_scaled = self.scaler.transform(features)
        
        # Get prediction probability
        risk_prob = self.model.predict_proba(features_scaled)[0][1]
        
        # Define risk levels
        risk_message = {
            (0.0, 0.3): "Low risk of network outage",
            (0.3, 0.7): "Moderate risk of network outage",
            (0.7, 1.0): "High risk of network outage"
        }
        
        # Get appropriate message
        for (lower, upper), message in risk_message.items():
            if lower <= risk_prob < upper:
                status_message = message
                break
        
        return {
            "risk_score": float(risk_prob),
            "confidence": float(self.model.score(features_scaled, [0])),  # Simple confidence score
            "message": status_message
        }