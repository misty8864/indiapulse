"""
Simple model training script for IndiaPulse.
Creates a demo XGBoost model trained on synthetic data.

For production: Replace with your actual PostgreSQL data loading.
"""

import pickle
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

def create_demo_model(output_dir: str = "./models"):
    """
    Create and train a demo XGBoost model with synthetic data.
    This is for testing purposes. Replace with real data in production.
    """
    
    # Create models directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating synthetic training data...")
    
    # Generate realistic synthetic data
    np.random.seed(42)
    n_samples = 1000
    
    # Create features with some patterns
    momentum_5d = np.random.normal(0.02, 0.03, n_samples)
    momentum_20d = np.random.normal(0.01, 0.02, n_samples)
    volatility_10d = np.random.exponential(0.02, n_samples)
    avg_daily_return = np.random.normal(0.001, 0.015, n_samples)
    volume_10d = np.random.exponential(1000000, n_samples)
    
    X = np.column_stack([
        momentum_5d,
        momentum_20d,
        volatility_10d,
        avg_daily_return,
        volume_10d
    ])
    
    # Create target with some correlation to momentum features
    y = ((momentum_5d + momentum_20d) > 0.01).astype(int)
    
    # Add some noise
    noise_idx = np.random.choice(len(y), size=int(0.1 * len(y)), replace=False)
    y[noise_idx] = 1 - y[noise_idx]
    
    print(f"Training data shape: {X.shape}")
    print(f"Class distribution - 0: {(y==0).sum()}, 1: {(y==1).sum()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\nTraining XGBoost model...")
    
    # Create and train pipeline
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            verbosity=0
        ))
    ])
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    
    print(f"\nModel Performance on Test Set:")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    
    # Save model
    model_path = os.path.join(output_dir, "sector_momentum_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\n✅ Model saved to: {model_path}")
    print(f"   File size: {os.path.getsize(model_path) / 1024:.2f} KB")
    
    return model_path

if __name__ == "__main__":
    model_path = create_demo_model()
    print(f"\nReady to use! Model location: {model_path}")