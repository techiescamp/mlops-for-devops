import pandas as pd
from pathlib import Path
from datetime import datetime, timezone


def process_data():
    # Paths
    SCRIPT_DIR = Path(__file__).parent.resolve()
    PROJECT_ROOT = SCRIPT_DIR.parent.parent

    CSV_PATH = PROJECT_ROOT / "phase-1-local-dev/datasets/employee_attrition.csv"
    OUTPUT_PATH = SCRIPT_DIR / "data/employee_attrition_features.parquet"

    OUTPUT_PATH.parent.mkdir(exist_ok=True)

    # Read CSV
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}\n")

    # ============================================================
    # Encode categorical columns
    # ============================================================

    # Binary mappings (Yes/No)
    binary_map = {"Yes": 1, "No": 0}
    df["Overtime"] = df["Overtime"].map(binary_map)
    df["Remote Work"] = df["Remote Work"].map(binary_map)
    df["Leadership Opportunities"] = df["Leadership Opportunities"].map(binary_map)
    df["Innovation Opportunities"] = df["Innovation Opportunities"].map(binary_map)

    # Gender
    df["Gender"] = df["Gender"].map({"Male": 1, "Female": 0})

    # Attrition (target)
    df["Attrition"] = df["Attrition"].map({"Left": 1, "Stayed": 0})

    # Ordinal mappings (Low → High)
    rating_map = {"Low": 1, "Medium": 2, "High": 3}
    df["Job Satisfaction"] = df["Job Satisfaction"].map(rating_map)
    df["Employee Recognition"] = df["Employee Recognition"].map(rating_map)

    performance_map = {"Low": 1, "Average": 2, "High": 3}
    df["Performance Rating"] = df["Performance Rating"].map(performance_map)

    balance_map = {"Poor": 1, "Fair": 2, "Good": 3, "Excellent": 4}
    df["Work-Life Balance"] = df["Work-Life Balance"].map(balance_map)
    df["Company Reputation"] = df["Company Reputation"].map(balance_map)

    # Education Level
    education_map = {
        "High School": 1,
        "Associate Degree": 2,
        "Bachelor's Degree": 3,
        "Master's Degree": 4,
        "PhD": 5
    }
    df["Education Level"] = df["Education Level"].map(education_map)

    # Job Level
    job_level_map = {"Entry": 1, "Mid": 2, "Senior": 3}
    df["Job Level"] = df["Job Level"].map(job_level_map)

    # Company Size
    company_size_map = {"Small": 1, "Medium": 2, "Large": 3}
    df["Company Size"] = df["Company Size"].map(company_size_map)

    # Marital Status
    marital_map = {"Single": 1, "Married": 2, "Divorced": 3}
    df["Marital Status"] = df["Marital Status"].map(marital_map)

    # Job Role - label encode
    job_roles = df["Job Role"].unique()
    job_role_map = {role: idx for idx, role in enumerate(job_roles, 1)}
    df["Job Role"] = df["Job Role"].map(job_role_map)
    print(f"Job Role mapping: {job_role_map}\n")

    # ============================================================
    # Prepare for Feast
    # ============================================================

    # Rename columns to match Feast conventions
    df = df.rename(columns={
        "Employee ID": "employee_id",
        "Age": "age",
        "Gender": "gender",
        "Years at Company": "years_at_company",
        "Job Role": "job_role",
        "Monthly Income": "monthly_income",
        "Work-Life Balance": "work_life_balance",
        "Job Satisfaction": "job_satisfaction",
        "Performance Rating": "performance_rating",
        "Number of Promotions": "num_promotions",
        "Overtime": "overtime",
        "Distance from Home": "distance_from_home",
        "Education Level": "education_level",
        "Marital Status": "marital_status",
        "Number of Dependents": "num_dependents",
        "Job Level": "job_level",
        "Company Size": "company_size",
        "Company Tenure": "company_tenure",
        "Remote Work": "remote_work",
        "Leadership Opportunities": "leadership_opportunities",
        "Innovation Opportunities": "innovation_opportunities",
        "Company Reputation": "company_reputation",
        "Employee Recognition": "employee_recognition",
        "Attrition": "attrition",
    })

    # Add timestamp columns required by Feast
    now = datetime.now(tz=timezone.utc)
    df["event_timestamp"] = now
    df["created"] = now

    # Drop dataset_type column (not needed for features)
    df = df.drop(columns=["dataset_type"], errors="ignore")

    # Select only needed columns
    feature_columns = [
        "employee_id",
        "age",
        "gender",
        "years_at_company",
        "job_role",
        "monthly_income",
        "work_life_balance",
        "job_satisfaction",
        "performance_rating",
        "num_promotions",
        "overtime",
        "distance_from_home",
        "education_level",
        "marital_status",
        "num_dependents",
        "job_level",
        "company_size",
        "company_tenure",
        "remote_work",
        "leadership_opportunities",
        "innovation_opportunities",
        "company_reputation",
        "employee_recognition",
        "attrition",
        "event_timestamp",
        "created",
    ]

    df = df[feature_columns]

    # Save to parquet
    df.to_parquet(OUTPUT_PATH, index=False)

    print("Sample data:")
    print(df.head(3).to_string(index=False))
    print(f"\n✅ Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    process_data()