from pathlib import Path
import os

# Root of the project
BASE_DIR = Path(__file__).resolve().parents[2]

# Dataset directories
DATASET_DIR = BASE_DIR / "datasets"
RAW_DATA_PATH = DATASET_DIR / "employee_attrition.csv"

# Data preparation
DATA_PREP_DIR = DATASET_DIR / "processed"
INGESTION_PATH = DATA_PREP_DIR / "raw_ingested.csv"
VALIDATION_PATH = DATA_PREP_DIR / "validated.csv"
EDA_PATH = DATA_PREP_DIR / "eda.csv"
CLEANING_PATH = DATA_PREP_DIR / "cleaned.csv"
FEATURED_PATH = DATA_PREP_DIR / "featured.csv"
PREPROCESSED_TRAIN_PATH = DATA_PREP_DIR / "train.csv"
PREPROCESSED_TEST_PATH = DATA_PREP_DIR / "test.csv"


# Model artifacts
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "model.pkl"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"

# Ensure directories exist
os.makedirs(DATA_PREP_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)
