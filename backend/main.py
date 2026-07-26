"""
This module serves as the primary inference engine and explainability layer. 
It loads all saved model artifacts (.joblib, .h5) into memory at startup to 
eliminate load times during inference. It exposes endpoints for real-time log 
evaluation, dataset statistics, and generates structured, human-readable 
explanations for security analysts, detailing why an anomaly was flagged.
"""

import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf


app = FastAPI(
    title="Cybersecurity Anomaly Detection AI Engine",
    version="1.0.0",
    description="FastAPI microservice for real-time threat detection and anomaly explainability."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MODEL_DIR = os.path.join("..", "ml-engine", "saved_models")
DATASET_DIR = os.path.join("..", "synthetic-data", "exports")

models = {
    "encoders": None,
    "scaler": None,
    "scaler_fails": None,  
    "scaler_time": None,   
    "svm": None,
    "lstm": None,
    "label_encoder": None
}


class LogEvent(BaseModel):
    entity_id: str = Field(..., example="usr_mkt_014")
    entity_type: str = Field(..., example="user")
    timestamp: str = Field(..., example="2026-07-26T03:15:00")
    source_ip: str = Field(..., example="185.220.101.5")
    geo_location: str = Field("Unknown / Datacenter", example="Tokyo, Japan")
    resource_accessed: str = Field(..., example="/finance/db_backup_chunk")
    auth_method: str = Field(..., example="password")
    session_duration: float = Field(..., example=400.0)
    command_sequence: List[str] = Field(default_factory=list, example=["GET /finance/db_backup_chunk"])
    device_fingerprint: str = Field(..., example="Android 11 | Spoofed Build v4.1")


class SequencePredictionRequest(BaseModel):
    logs: List[LogEvent] = Field(..., min_items=1, max_items=10)


@app.on_event("startup")
async def load_artifacts():
    """Loads preprocessor rules and trained weights into RAM once on startup."""
    print("Loading machine learning models and encoders into memory...") 
    
    try:
        models["encoders"] = joblib.load(os.path.join(MODEL_DIR, "encoders.joblib"))
        models["label_encoder"] = joblib.load(
    os.path.join(MODEL_DIR, "label_encoder.joblib")
)
        print("Available classes:")
        print(models["label_encoder"].classes_)
        models["scaler"] = joblib.load(os.path.join(MODEL_DIR, "scaler.joblib"))
        models["scaler_fails"] = joblib.load(os.path.join(MODEL_DIR, "scaler_fails.joblib")) 
        models["scaler_time"] = joblib.load(os.path.join(MODEL_DIR, "scaler_time.joblib")) 
        models["svm"] = joblib.load(os.path.join(MODEL_DIR, "one_class_svm.joblib"))
        models["label_encoder"] = joblib.load(os.path.join(MODEL_DIR, "label_encoder.joblib"))
        models["lstm"] = tf.keras.models.load_model(os.path.join(MODEL_DIR, "lstm_sequence_model.h5"))
        print("All models successfully loaded into memory!")
    except Exception as e:
        print(f"Warning: Failed to load one or more model artifacts: {e}")



def transform_log(log: LogEvent, time_delta: float = 0.0) -> np.ndarray:
    """Translates a raw input log JSON into the complete 9-feature numerical vector."""
    encoders = models["encoders"]
    scaler = models["scaler"]

    dt = pd.to_datetime(log.timestamp)
    hour = dt.hour

    def safe_encode(encoder, value):
        if value in encoder.classes_:
            return encoder.transform([value])[0] 
        return 0

    e_id = safe_encode(encoders['entity_id'], log.entity_id)
    ip = safe_encode(encoders['source_ip'], log.source_ip)
    res = safe_encode(encoders['resource_accessed'], log.resource_accessed)
    auth = safe_encode(encoders['auth_method'], log.auth_method)
    dev = safe_encode(encoders['device_fingerprint'], log.device_fingerprint)

    # Scale session duration and hour of day (Features 6 & 7)
    scaled_num = scaler.transform([[log.session_duration, hour]])[0]
    duration_scaled, hour_scaled = scaled_num[0], scaled_num[1]

    # Extract and scale the 8th feature dynamically (Failed Auths)
    failed_auth_count = sum(1 for cmd in log.command_sequence if "FAILED" in cmd)
    fails_scaled = models["scaler_fails"].transform([[failed_auth_count]])[0][0]

    # Extract and scale the 9th feature dynamically (Time Delta)
    time_scaled = models["scaler_time"].transform([[time_delta]])[0][0]

    return np.array([e_id, ip, res, auth, dev, duration_scaled, hour_scaled, fails_scaled, time_scaled])



def generate_explanation(log: LogEvent, predicted_class: str, confidence: float) -> dict:
    """
    Evaluates the event attributes and generates structured, human-readable 
    explanations for SOC analysts detailing why the alert was generated.
    """
    reasons = []
    dt = pd.to_datetime(log.timestamp)

    if 1 <= dt.hour <= 4:
        reasons.append(f"Unusual activity timing detected at {dt.strftime('%H:%M')} AM (Off-hours window).")

    sensitive_paths = ["/admin", "/root", "/finance", "/export", "/db_backup"]
    if any(path in log.resource_accessed for path in sensitive_paths):
        reasons.append(f"Accessed restricted critical resource target: '{log.resource_accessed}'.")

    if "Spoofed" in log.device_fingerprint or "Curl" in log.device_fingerprint:
        reasons.append(f"Suspicious client agent or unverified device fingerprint: '{log.device_fingerprint}'.")

    if "Unknown" in log.geo_location or log.source_ip.startswith("185.") or log.source_ip.startswith("45."):
        reasons.append(f"Source IP ({log.source_ip}) associated with unverified proxy or external subnet ({log.geo_location}).")

    if any("FAILED" in cmd for cmd in log.command_sequence):
        reasons.append("Command telemetry indicates multiple failed authentication attempts.")

    if not reasons:
        reasons.append("Behavioral profile deviated significantly from learned cluster center.")

    return {
        "alert_type": predicted_class,
        "confidence_score": round(float(confidence), 4),
        "primary_triggers": reasons,
        "recommended_action": "Isolate entity session and flag for SOC tier-2 review." if predicted_class != "normal" else "No action required."
    }


# --- API ENDPOINTS ---

@app.get("/api/health")
async def health_check():
    return {
        "status": "Operational",
        "models_loaded": all(v is not None for v in models.values()),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/stats/distribution")
async def get_data_distribution():
    """
    Reads the final dataset and returns the actual class distributions 
    to populate the UI overview sidebar.
    """
    try:
        dataset_path = os.path.join(DATASET_DIR, "final_training_dataset.csv")
        df = pd.read_csv(dataset_path)
        
        counts = df['label'].value_counts().to_dict()
        total = len(df)
        
        return {
            "total_sequences": total,
            "class_distribution": counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dataset distribution: {str(e)}")


@app.post("/api/predict/single")
async def predict_single_log(log: LogEvent):
    """
    Evaluates a single log against the One-Class SVM baseline model.
    """
    if models["svm"] is None:
        raise HTTPException(status_code=503, detail="Models are not initialized.")

    feature_vector = transform_log(log)[:7].reshape(1, -1)
    prediction = models["svm"].predict(feature_vector)[0]
    
    is_anomaly = bool(prediction == -1)
    status_label = "ANOMALY DETECTED" if is_anomaly else "NORMAL"

    explanation = generate_explanation(
        log, 
        predicted_class="Unusual Behavioral Deviation" if is_anomaly else "normal", 
        confidence=0.87 if is_anomaly else 0.99
    )

    return {
        "status": status_label,
        "is_anomaly": is_anomaly,
        "svm_prediction_code": int(prediction),
        "explanation": explanation
    }


@app.post("/api/predict/sequence")
async def predict_log_sequence(request: SequencePredictionRequest):
    """
    Evaluates a sequence of 5 chronological logs using the Bi-LSTM deep learning model.
    """
    if models["lstm"] is None:
        raise HTTPException(status_code=503, detail="Sequence model not initialized.")

    raw_logs = request.logs
    if len(raw_logs) < 5:
        raw_logs = [raw_logs[0]] * (5 - len(raw_logs)) + raw_logs

    recent_logs = raw_logs[-5:]
    
    feature_matrix = []
    for i, log in enumerate(recent_logs):
        if i == 0:
            delta = 0.0
        else:
            dt_curr = pd.to_datetime(log.timestamp)
            dt_prev = pd.to_datetime(recent_logs[i-1].timestamp)
            delta = (dt_curr - dt_prev).total_seconds()
            
        feature_matrix.append(transform_log(log, delta))
        
    input_tensor = np.expand_dims(np.array(feature_matrix), axis=0)

    probabilities = models["lstm"].predict(input_tensor)[0]
    predicted_class_idx = np.argmax(probabilities)
    confidence = probabilities[predicted_class_idx]
    
    predicted_label = models["label_encoder"].classes_[predicted_class_idx]

    last_log = recent_logs[-1]
    explanation = generate_explanation(last_log, predicted_label, confidence)

    return {
        "status": "ANOMALY DETECTED" if predicted_label != "normal" else "NORMAL",
        "predicted_attack_type": predicted_label,
        "confidence_score": float(confidence),
        "all_probabilities": {
            cls: float(prob) for cls, prob in zip(models["label_encoder"].classes_, probabilities)
        },
        "explanation": explanation
    }