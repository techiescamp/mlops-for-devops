from pathlib import Path
import os

# Root of the project
BASE_DIR = Path(__file__).resolve().parents[2]

# Dataset directories
DATASET_DIR = BASE_DIR / "datasets"
RAW_DATA_PATH = DATASET_DIR / "employee_attrition.csv"

# Data preparation
DATA_PREP_DIR = DATASET_DIR / "data-preparation"
INGESTION_PATH = DATA_PREP_DIR / "01_ingestion.csv"
VALIDATION_PATH = DATA_PREP_DIR / "02_validation.csv"
EDA_PATH = DATA_PREP_DIR / "03_eda_df.csv"
CLEANING_PATH = DATA_PREP_DIR / "04_cleaning.csv"
FEATURED_PATH = DATA_PREP_DIR / "05_feature_engg_df.csv"
PREPROCESSED_TRAIN_PATH = DATA_PREP_DIR / "06_train_df.csv"
PREPROCESSED_TEST_PATH = DATA_PREP_DIR / "06_test_df.csv"


# Model artifacts
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "model.pkl"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"

# Ensure directories exist
os.makedirs(DATA_PREP_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)
