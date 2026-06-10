from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
import pickle
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IndiaPulse Sector Momentum API",
    description="Real-time ML predictions for Indian stock market sector momentum",
    version="1.0.0"
)

# CORS middleware for external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model cache
_model = None
_model_loaded_at = None

# Pydantic models for request/response
class PredictionRequest(BaseModel):
    """Request model for predictions"""
    momentum_5d: float = Field(..., description="5-day momentum")
    momentum_20d: float = Field(..., description="20-day momentum")
    volatility_10d: float = Field(..., description="10-day volatility")
    avg_daily_return: float = Field(..., description="Average daily return")
    volume_10d: float = Field(..., description="10-day average volume")

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    prediction: int = Field(..., description="Binary prediction (0 or 1)")
    confidence: float = Field(..., description="Prediction confidence score")
    features_used: Dict[str, float] = Field(..., description="Features used for prediction")
    timestamp: str = Field(..., description="Prediction timestamp")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_loaded_at: str = None
    timestamp: str

class ModelInfoResponse(BaseModel):
    """Model information response"""
    name: str
    version: str
    features: list
    feature_count: int
    model_type: str
    trained_on_samples: int = 0

class MetricsResponse(BaseModel):
    """Metrics response"""
    total_predictions: int
    avg_inference_time_ms: float
    model_status: str
    last_updated: str

# Global metrics tracker
class MetricsTracker:
    def __init__(self):
        self.total_predictions = 0
        self.inference_times = []
        self.last_updated = datetime.utcnow().isoformat()
    
    def record_prediction(self, inference_time: float):
        self.total_predictions += 1
        self.inference_times.append(inference_time)
        self.last_updated = datetime.utcnow().isoformat()
    
    def get_avg_inference_time(self) -> float:
        if not self.inference_times:
            return 0.0
        return sum(self.inference_times) / len(self.inference_times)

metrics = MetricsTracker()

def load_model():
    """Load XGBoost model from pickle file"""
    global _model, _model_loaded_at
    
    if _model is not None:
        return _model
    
    # Try multiple possible model paths (ordered by likelihood)
    possible_paths = [
        "/app/models/sector_momentum_model.pkl",  # Railway/Docker standard
        "./models/sector_momentum_model.pkl",  # Local
        "../../../models/sector_momentum_model.pkl",  # From api/main.py
        "models/sector_momentum_model.pkl",  # Relative to current dir
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    _model = pickle.load(f)
                    _model_loaded_at = datetime.utcnow().isoformat()
                    logger.info(f"Model loaded successfully from {path}")
                    return _model
            except Exception as e:
                logger.error(f"Error loading model from {path}: {e}")
                continue
    
    # If no pickle found, create a mock model for testing
    logger.warning("No model file found. Using mock model for testing.")
    return None

# Load model on startup
load_model()

@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "IndiaPulse Sector Momentum API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "model_info": "/model/info",
            "predict": "/predict",
            "metrics": "/metrics"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["monitoring"])
async def health_check():
    """Check API and model health"""
    return {
        "status": "healthy" if _model is not None else "degraded",
        "model_loaded": _model is not None,
        "model_loaded_at": _model_loaded_at,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/model/info", response_model=ModelInfoResponse, tags=["model"])
async def model_info():
    """Get model metadata and information"""
    return {
        "name": "Sector Momentum Classifier",
        "version": "1.0.0",
        "features": [
            "momentum_5d",
            "momentum_20d",
            "volatility_10d",
            "avg_daily_return",
            "volume_10d"
        ],
        "feature_count": 5,
        "model_type": "XGBoost Pipeline (StandardScaler + XGBClassifier)",
        "trained_on_samples": 0
    }

@app.post("/predict", response_model=PredictionResponse, tags=["predictions"])
async def predict(request: PredictionRequest):
    """
    Make real-time prediction for sector momentum
    
    Returns binary classification (0: downward, 1: upward momentum)
    """
    
    if _model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Service temporarily unavailable."
        )
    
    try:
        import time
        start_time = time.time()
        
        # Prepare features in correct order
        features = [
            request.momentum_5d,
            request.momentum_20d,
            request.volatility_10d,
            request.avg_daily_return,
            request.volume_10d
        ]
        
        # Make prediction
        import numpy as np
        X = np.array([features])
        prediction = int(_model.predict(X)[0])
        
        # Get confidence (probability from the classifier)
        probabilities = _model.predict_proba(X)[0]
        confidence = float(max(probabilities))
        
        inference_time = (time.time() - start_time) * 1000  # Convert to ms
        metrics.record_prediction(inference_time)
        
        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "features_used": {
                "momentum_5d": request.momentum_5d,
                "momentum_20d": request.momentum_20d,
                "volatility_10d": request.volatility_10d,
                "avg_daily_return": request.avg_daily_return,
                "volume_10d": request.volume_10d
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/metrics", response_model=MetricsResponse, tags=["monitoring"])
async def get_metrics():
    """Get API metrics and performance statistics"""
    return {
        "total_predictions": metrics.total_predictions,
        "avg_inference_time_ms": round(metrics.get_avg_inference_time(), 2),
        "model_status": "loaded" if _model is not None else "not_loaded",
        "last_updated": metrics.last_updated
    }

@app.get("/status", tags=["monitoring"])
async def status():
    """Get detailed status"""
    return {
        "api_version": "1.0.0",
        "model_loaded": _model is not None,
        "predictions_served": metrics.total_predictions,
        "uptime_status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")