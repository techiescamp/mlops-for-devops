from fastapi import FastAPI
from src.schemas import EmployeeFeatures, PredictionResponse
from src.predictor import Predictor

app = FastAPI(title="Attrition Prediction Service", version="1.0.0")
predictor = Predictor()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready", "model_loaded": predictor.is_loaded()}


@app.post("/predict", response_model=PredictionResponse)
def predict(features: EmployeeFeatures):
    result = predictor.predict(features.to_model_input())
    return result