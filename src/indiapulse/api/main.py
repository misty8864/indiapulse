import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
from datetime import datetime
from sqlalchemy import text
from indiapulse.db.connection import engine

# Load model directly from file
MODEL_PATH = "C:/Users/SBDiv/indiapulse/mlruns/1/models/m-6c9da6dee5d644e990d458971aa3412a/artifacts/model.pkl"

app = FastAPI(title="IndiaPulse Sector Momentum API", version="0.1.0")

# Load model on startup
model = None
model_info = None

@app.on_event("startup")
def load_model():
    global model, model_info
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        model_info = {
            "model_type": "XGBoost Classifier with StandardScaler",
            "accuracy": 0.5094,
            "features": ["momentum_5d", "momentum_20d", "volatility_10d", "avg_daily_return", "volume_10d"]
        }
        print("✅ Model loaded successfully from file")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

# Request/Response Models
class PredictRequest(BaseModel):
    sector: str
    momentum_5d: float
    momentum_20d: float
    volatility_10d: float
    avg_daily_return: float
    volume_10d: float

class PredictResponse(BaseModel):
    sector: str
    prediction: int
    confidence: float
    message: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

class ModelInfoResponse(BaseModel):
    model_type: str
    accuracy: float
    features: list

class MetricsResponse(BaseModel):
    total_predictions: int
    avg_confidence: float
    up_predictions: int
    down_predictions: int

# Helper function to log prediction
def log_prediction(sector, momentum_5d, momentum_20d, volatility_10d, avg_daily_return, volume_10d, prediction, confidence):
    try:
        with engine.begin() as conn:
            sql = text("""
                INSERT INTO predictions_log 
                (sector, momentum_5d, momentum_20d, volatility_10d, avg_daily_return, volume_10d, prediction, confidence)
                VALUES (:sector, :momentum_5d, :momentum_20d, :volatility_10d, :avg_daily_return, :volume_10d, :prediction, :confidence)
            """)
            conn.execute(sql, {
                "sector": sector,
                "momentum_5d": momentum_5d,
                "momentum_20d": momentum_20d,
                "volatility_10d": volatility_10d,
                "avg_daily_return": avg_daily_return,
                "volume_10d": volume_10d,
                "prediction": prediction,
                "confidence": confidence
            })
    except Exception as e:
        print(f"❌ Failed to log prediction: {e}")

# Endpoints
@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.get("/model/info", response_model=ModelInfoResponse)
def get_model_info():
    """Get model information"""
    if model_info is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return model_info

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """Predict next day momentum direction for a sector"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare features in correct order
        features = [[
            request.momentum_5d,
            request.momentum_20d,
            request.volatility_10d,
            request.avg_daily_return,
            request.volume_10d
        ]]
        
        # Get prediction and probability
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = max(probabilities) * 100
        
        # Log the prediction
        log_prediction(
            request.sector,
            request.momentum_5d,
            request.momentum_20d,
            request.volatility_10d,
            request.avg_daily_return,
            request.volume_10d,
            int(prediction),
            float(confidence)
        )
        
        return {
            "sector": request.sector,
            "prediction": int(prediction),
            "confidence": round(confidence, 2),
            "message": f"Next day {'UP' if prediction == 1 else 'DOWN'} with {confidence:.2f}% confidence"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    """Get prediction metrics for monitoring"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        with engine.begin() as conn:
            # Total predictions
            total = conn.execute(text("SELECT COUNT(*) FROM predictions_log;")).scalar()
            
            # Avg confidence
            avg_conf = conn.execute(text("SELECT AVG(confidence) FROM predictions_log;")).scalar()
            
            # UP vs DOWN split
            up_count = conn.execute(text("SELECT COUNT(*) FROM predictions_log WHERE prediction = 1;")).scalar()
            down_count = conn.execute(text("SELECT COUNT(*) FROM predictions_log WHERE prediction = 0;")).scalar()
            
            return {
                "total_predictions": total or 0,
                "avg_confidence": round(float(avg_conf), 2) if avg_conf else 0,
                "up_predictions": up_count or 0,
                "down_predictions": down_count or 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics fetch failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
