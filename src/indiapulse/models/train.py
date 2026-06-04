import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

DB_URL = "postgresql+psycopg2://indiapulse_user:changeme_local@localhost:5432/indiapulse"

def load_features():
    engine = create_engine(DB_URL)
    df = pd.read_sql("SELECT * FROM analytics.mart_ml_features", engine)
    df = df.dropna()
    return df

def train():
    mlflow.set_experiment("sector-momentum")
    df = load_features()
    feature_cols = ["momentum_5d", "momentum_20d", "volatility_10d",
                    "avg_daily_return", "volume_10d"]
    X = df[feature_cols]
    y = (df["next_day_return"] > 0).astype(int)
    tscv = TimeSeriesSplit(n_splits=5)
    with mlflow.start_run():
        params = {"n_estimators": 100, "max_depth": 4,
                  "learning_rate": 0.1, "random_state": 42}
        mlflow.log_params(params)
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", XGBClassifier(**params))
        ])
        scores = []
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            model.fit(X_train, y_train)
            preds = model.predict(X_val)
            scores.append(accuracy_score(y_val, preds))
        mean_acc = np.mean(scores)
        mlflow.log_metric("mean_cv_accuracy", mean_acc)
        mlflow.sklearn.log_model(model, "sector_momentum_model")
        print(f"Mean CV Accuracy: {mean_acc:.4f}")

if __name__ == "__main__":
    train()