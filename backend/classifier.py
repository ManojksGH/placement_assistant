# backend/classifier.py
import os
import joblib
from typing import Any, Dict
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "model.joblib"

def load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None

def save_model(model):
    joblib.dump(model, MODEL_PATH)

def predict(text: str) -> Dict[str, Any]:
    model = load_model()
    if not model:
        return {"label": "general", "confidence": 0.0, "error": "no_model"}
    prob = None
    label = None
    X = [text]
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            idx = proba.argmax()
            label = model.classes_[idx]
            prob = float(proba[idx])
        else:
            label = model.predict(X)[0]
            prob = None
    except Exception as e:
        return {"label": "general", "confidence": 0.0, "error": str(e)}
    return {"label": label, "confidence": prob}
