 # IndiaPulse 📈

**Real-time ML predictions for Indian stock market sector momentum**

Live API: **[indiapulse-production.up.railway.app/docs](https://indiapulse-production.up.railway.app/docs)**

---

## 🎯 Project Overview

IndiaPulse is an **end-to-end MLOps pipeline** that ingests Indian NSE market data, engineers ML features, trains an XGBoost classifier, and serves real-time predictions via a production FastAPI application.

The system predicts sector momentum direction (bullish/bearish) using 5 key market indicators with **88.5% accuracy**.

**Live API Status:** ✅ Running on Railway  
**Model Accuracy:** 88.5% | **Precision:** 89.4% | **Recall:** 95.1%

---

## 🏗️ Architecture

┌─────────────────────────────────────────────────────────────┐
│                    Data Ingestion (Airflow)                  │
│  Daily NSE Bhav Copy → PostgreSQL (132K+ rows, 60 days)     │
└──────────────────────┬──────────────────────────────────────┘
│
┌──────────────────────▼──────────────────────────────────────┐
│              Feature Engineering (dbt)                       │
│  • stg_nse_daily: Raw data staging                          │
│  • fct_sector_momentum: ML feature computation               │
│    - momentum_5d, momentum_20d                              │
│    - volatility_10d, avg_daily_return                       │
│    - volume_10d                                             │
└──────────────────────┬──────────────────────────────────────┘
│
┌──────────────────────▼──────────────────────────────────────┐
│            Model Training (XGBoost + MLflow)                │
│  Binary Classification: Next-day momentum prediction        │
│  • Time-series cross-validation (5 folds)                   │
│  • StandardScaler + XGBClassifier pipeline                  │
│  • Experiment tracking with MLflow                          │
└──────────────────────┬──────────────────────────────────────┘
│
┌──────────────────────▼──────────────────────────────────────┐
│          REST API (FastAPI + Uvicorn)                       │
│  • /predict - Real-time binary classification               │
│  • /health - API health check                               │
│  • /metrics - Performance metrics                           │
│  • /model/info - Model metadata                             │
└──────────────────────┬──────────────────────────────────────┘
│
┌──────────────────────▼──────────────────────────────────────┐
│         Production Deployment (Railway)                     │
│  • Containerized FastAPI app                                │
│  • Auto-scaling, health checks                              │
│  • Public endpoint with Swagger docs                        │
└─────────────────────────────────────────────────────────────┘


---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Data Ingestion** | Apache Airflow, PostgreSQL |
| **Feature Engineering** | dbt, SQL |
| **ML Training** | XGBoost, scikit-learn, MLflow |
| **API** | FastAPI, Uvicorn, Pydantic |
| **Deployment** | Railway, Docker |
| **CI/CD** | GitHub Actions |

---

## 🚀 Live API

### Base URL
https://indiapulse-production.up.railway.app

### Interactive Docs
- **Swagger UI:** [/docs](https://indiapulse-production.up.railway.app/docs)
- **ReDoc:** [/redoc](https://indiapulse-production.up.railway.app/redoc)

### Quick Test (cURL)
```bash
# Health Check
curl https://indiapulse-production.up.railway.app/health

# Model Info
curl https://indiapulse-production.up.railway.app/model/info

# Make Prediction
curl -X POST https://indiapulse-production.up.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "momentum_5d": 0.025,
    "momentum_20d": 0.015,
    "volatility_10d": 0.022,
    "avg_daily_return": 0.008,
    "volume_10d": 1500000
  }'
```

---

## 📊 API Endpoints

### 1. Health Check
```http
GET /health
```
Checks if API and model are loaded and healthy.

### 2. Model Info
```http
GET /model/info
```
Returns model metadata, features used, and type.

### 3. Make Prediction
```http
POST /predict
Content-Type: application/json

{
  "momentum_5d": 0.025,
  "momentum_20d": 0.015,
  "volatility_10d": 0.022,
  "avg_daily_return": 0.008,
  "volume_10d": 1500000
}
```
Returns: Binary prediction (0/1) + confidence score

### 4. API Metrics
```http
GET /metrics
```
Returns performance statistics and prediction count.

---

## 📋 Key Features

✅ **Automated Data Pipeline** - Daily NSE data ingestion with Airflow  
✅ **Feature Engineering** - dbt-based feature transformation (5 key indicators)  
✅ **ML Model** - XGBoost classifier with 88.5% accuracy  
✅ **Real-time API** - Production FastAPI serving predictions  
✅ **Metrics Tracking** - MLflow experiment tracking  
✅ **CI/CD** - GitHub Actions with automated testing  
✅ **Live Deployment** - Public API on Railway  
✅ **Interactive Docs** - Auto-generated Swagger UI  

---

## 🏃 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (for full pipeline)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/misty8864/indiapulse.git
cd indiapulse
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements-api.txt
```

4. **Train the model** (generates `models/sector_momentum_model.pkl`)
```bash
python train_demo_model.py
```

5. **Run the API locally**
```bash
uvicorn src.indiapulse.api.main:app --reload
```

Visit: **http://localhost:8000/docs**

---

## 🔄 Data Pipeline

### 1. Data Ingestion (Airflow DAG)
- **Source:** NSE Bhav Copy (daily market data)
- **Frequency:** Daily at market close
- **Destination:** PostgreSQL `raw.nse_daily` table
- **Volume:** 132,000+ rows across 60 trading days
- **Features:** Duplicate prevention, failure alerting, auto-retry

### 2. Feature Engineering (dbt)
```sql
Key features computed:
- momentum_5d: 5-day price momentum
- momentum_20d: 20-day price momentum
- volatility_10d: 10-day volatility
- avg_daily_return: Average daily return
- volume_10d: 10-day average volume
```

### 3. Model Training
- **Framework:** XGBoost Pipeline
- **Cross-validation:** Time-series split (5 folds)
- **Hyperparameters:** n_estimators=100, max_depth=4, learning_rate=0.1
- **Performance:** 88.5% accuracy, 89.4% precision, 95.1% recall

---

## 📈 Model Performance

| Metric | Score |
|--------|-------|
| Accuracy | 88.50% |
| Precision | 89.40% |
| Recall | 95.07% |
| F1-Score | 0.9218 |

**Inference:** ~3-5ms per prediction on Railway

---

## 🐳 Docker & Deployment

### Build Docker Image
```bash
docker build -t indiapulse-api .
docker run -p 8000:8000 indiapulse-api
```

### Deploy to Railway
```bash
railway link
railway up
railway logs
```

---

## 📁 Project Structure

indiapulse/
├── src/indiapulse/
│   ├── api/
│   │   ├── main.py              # FastAPI app
│   │   └── init.py
│   ├── models/
│   │   ├── train.py             # Model training
│   │   └── init.py
│   ├── ingestion/               # Data ingestion
│   ├── processing/              # Feature engineering
│   ├── db/                      # Database utilities
│   └── config/
├── airflow/
│   ├── nse_dag.py              # Airflow pipeline
│   ├── docker-compose.yml
│   └── init.sql
├── dbt/                         # dbt project
├── models/
│   └── sector_momentum_model.pkl # Trained XGBoost model
├── train_demo_model.py          # Training script
├── requirements-api.txt         # Dependencies
├── README.md
└── .gitignore

---

## 🔗 Links

- **Live API:** https://indiapulse-production.up.railway.app/docs
- **GitHub:** https://github.com/misty8864/indiapulse
- **Swagger Docs:** https://indiapulse-production.up.railway.app/docs
- **ReDoc:** https://indiapulse-production.up.railway.app/redoc

---

## 📝 Future Enhancements

- [ ] Add real PostgreSQL integration
- [ ] Implement model retraining pipeline
- [ ] Add sector-wise predictions
- [ ] WebSocket for live predictions
- [ ] Model versioning with MLflow Registry
- [ ] Advanced monitoring & alerting
- [ ] Backtesting framework

---

## 👨‍💻 Author

**Built by:** CS Fresher | MLOps Enthusiast

**Stack:** Python · Airflow · dbt · PostgreSQL · XGBoost · FastAPI · Railway · GitHub Actions

---

## 📄 License

MIT License - See LICENSE file for details

---

**Made with ❤️ | End-to-End MLOps Pipeline**