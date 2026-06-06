from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import pickle
import numpy as np
from datetime import datetime
import logging

# Database connection
from indiapulse.db.connection import engine
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="IndiaPulse Sector Momentum API",
    description="Real-time ML predictions for Indian stock market sector momentum",
    version="0.1.0"
)

# Global model variable
model = None
model_loaded = False
model_info = {
    "type": "XGBoost Classifier",
    "accuracy": 0.51,
    "features": [
        "momentum_5d",
        "momentum_20d",
        "volatility_10d",
        "avg_daily_return",
        "volume_10d"
    ]
}

# Request/Response Models
class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

class ModelInfoResponse(BaseModel):
    detail: str

class PredictionRequest(BaseModel):
    sector: str
    momentum_5d: float
    momentum_20d: float
    volatility_10d: float
    avg_daily_return: float
    volume_10d: float

class PredictionResponse(BaseModel):
    sector: str
    prediction: str
    confidence: float
    timestamp: str

class MetricsResponse(BaseModel):
    total_predictions: int
    avg_confidence: float
    up_predictions: int
    down_predictions: int

# Load model on startup
def load_model():
    global model, model_loaded
    try:
        # Try multiple paths for model loading
        model_paths = [
            "mlruns/1/models/m-6c9da6dee5d644e990d458971aa3412a/artifacts/model.pkl",
            "./mlruns/1/models/m-6c9da6dee5d644e990d458971aa3412a/artifacts/model.pkl",
            "/app/mlruns/1/models/m-6c9da6dee5d644e990d458971aa3412a/artifacts/model.pkl",
        ]
        
        for path in model_paths:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    model = pickle.load(f)
                model_loaded = True
                logger.info(f"✅ Model loaded from {path}")
                return
        
        logger.warning("⚠️ Model file not found at any expected location")
        logger.warning(f"Expected paths: {model_paths}")
        logger.warning("API will work but /predict endpoint will fail without model")
        model_loaded = False
        
    except Exception as e:
        logger.error(f"❌ Error loading model: {str(e)}")
        model_loaded = False

# Load model on app startup
load_model()

# Endpoints

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if API is healthy and model is loaded"""
    return {
        "status": "healthy",
        "model_loaded": model_loaded
    }

@app.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get model metadata and information"""
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "detail": f"Model Type: {model_info['type']}, Accuracy: {model_info['accuracy']:.1%}, Features: {', '.join(model_info['features'])}"
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make a prediction for sector momentum"""
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare features in correct order
        features = np.array([
            request.momentum_5d,
            request.momentum_20d,
            request.volatility_10d,
            request.avg_daily_return,
            request.volume_10d
        ]).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(features)[0]
        confidence = float(model.predict_proba(features)[0].max())
        
        # Map prediction to UP/DOWN
        prediction_label = "UP" if prediction == 1 else "DOWN"
        
        # Log prediction to database
        try:
            with engine.connect() as conn:
                insert_stmt = text("""
                    INSERT INTO predictions_log 
                    (sector, momentum_5d, momentum_20d, volatility_10d, avg_daily_return, volume_10d, prediction, confidence, timestamp)
                    VALUES (:sector, :m5, :m20, :vol, :avg_ret, :vol_10, :pred, :conf, :ts)
                """)
                conn.execute(insert_stmt, {
                    "sector": request.sector,
                    "m5": request.momentum_5d,
                    "m20": request.momentum_20d,
                    "vol": request.volatility_10d,
                    "avg_ret": request.avg_daily_return,
                    "vol_10": request.volume_10d,
                    "pred": prediction_label,
                    "conf": confidence,
                    "ts": datetime.now()
                })
                conn.commit()
        except Exception as db_error:
            logger.warning(f"Could not log to database: {db_error}")
        
        return {
            "sector": request.sector,
            "prediction": prediction_label,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get prediction metrics and statistics"""
    try:
        with engine.connect() as conn:
            # Get total predictions
            total_result = conn.execute(text("SELECT COUNT(*) as count FROM predictions_log"))
            total = total_result.fetchone()[0] if total_result else 0
            
            # Get average confidence
            conf_result = conn.execute(text("SELECT AVG(confidence) as avg_conf FROM predictions_log"))
            avg_conf = float(conf_result.fetchone()[0]) if conf_result else 0.0
            
            # Get UP/DOWN split
            up_result = conn.execute(text("SELECT COUNT(*) as count FROM predictions_log WHERE prediction = 'UP'"))
            up_count = up_result.fetchone()[0] if up_result else 0
            
            down_result = conn.execute(text("SELECT COUNT(*) as count FROM predictions_log WHERE prediction = 'DOWN'"))
            down_count = down_result.fetchone()[0] if down_result else 0
            
            return {
                "total_predictions": total,
                "avg_confidence": avg_conf,
                "up_predictions": up_count,
                "down_predictions": down_count
            }
    except Exception as e:
        logger.warning(f"Metrics query failed: {e}")
        return {
            "total_predictions": 0,
            "avg_confidence": 0.0,
            "up_predictions": 0,
            "down_predictions": 0
        }

@app.get("/")
async def root():
    """Root endpoint - redirects to docs"""
    return {"message": "IndiaPulse API is running! Visit /docs for API documentation"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)