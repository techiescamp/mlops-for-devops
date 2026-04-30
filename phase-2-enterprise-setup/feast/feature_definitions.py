from datetime import timedelta
from pathlib import Path
from feast import Entity, FeatureView, Field, FileSource, FeatureService, ValueType
from feast.types import Int64

REPO_DIR = Path(__file__).parent

# ============================================================
# Entity
# ============================================================
employee = Entity(
    name="employee_id",
    join_keys=["employee_id"],
    value_type=ValueType.INT64,
    description="Unique employee identifier",
)

# ============================================================
# Data Source
# ============================================================
employee_source = FileSource(
    path=str(REPO_DIR / "data" / "employee_attrition_features.parquet"),
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

# ============================================================
# Feature View
# ============================================================
employee_features = FeatureView(
    name="employee_features",
    entities=[employee],
    ttl=timedelta(days=365),
    schema=[
        # Demographics
        Field(name="age", dtype=Int64, description="Employee age"),
        Field(name="gender", dtype=Int64, description="Gender (0=Female, 1=Male)"),
        Field(name="marital_status", dtype=Int64, description="Marital status (1=Single, 2=Married, 3=Divorced)"),
        Field(name="num_dependents", dtype=Int64, description="Number of dependents"),
        Field(name="education_level", dtype=Int64, description="Education (1=HS to 5=PhD)"),
        
        # Job info
        Field(name="job_role", dtype=Int64, description="Job role (encoded)"),
        Field(name="job_level", dtype=Int64, description="Job level (1=Entry, 2=Mid, 3=Senior)"),
        Field(name="monthly_income", dtype=Int64, description="Monthly income"),
        Field(name="years_at_company", dtype=Int64, description="Years at company"),
        Field(name="company_tenure", dtype=Int64, description="Company tenure"),
        Field(name="num_promotions", dtype=Int64, description="Number of promotions"),
        
        # Work conditions
        Field(name="overtime", dtype=Int64, description="Works overtime (0=No, 1=Yes)"),
        Field(name="remote_work", dtype=Int64, description="Remote work (0=No, 1=Yes)"),
        Field(name="distance_from_home", dtype=Int64, description="Distance from home"),
        Field(name="work_life_balance", dtype=Int64, description="Work-life balance (1=Poor to 4=Excellent)"),
        
        # Company & satisfaction
        Field(name="company_size", dtype=Int64, description="Company size (1=Small, 2=Medium, 3=Large)"),
        Field(name="company_reputation", dtype=Int64, description="Company reputation (1=Poor to 4=Excellent)"),
        Field(name="job_satisfaction", dtype=Int64, description="Job satisfaction (1=Low to 3=High)"),
        Field(name="performance_rating", dtype=Int64, description="Performance (1=Low, 2=Avg, 3=High)"),
        Field(name="employee_recognition", dtype=Int64, description="Recognition (1=Low to 3=High)"),
        
        # Opportunities
        Field(name="leadership_opportunities", dtype=Int64, description="Leadership opportunities (0=No, 1=Yes)"),
        Field(name="innovation_opportunities", dtype=Int64, description="Innovation opportunities (0=No, 1=Yes)"),
        
        # Target
        Field(name="attrition", dtype=Int64, description="Left company (0=Stayed, 1=Left)"),
    ],
    source=employee_source,
    online=True,
)

# ============================================================
# Feature Service (excludes target for inference)
# ============================================================
employee_attrition_service = FeatureService(
    name="employee_attrition_service",
    features=[
        employee_features[[
            "age", "gender", "marital_status", "num_dependents", "education_level",
            "job_role", "job_level", "monthly_income", "years_at_company", "company_tenure",
            "num_promotions", "overtime", "remote_work", "distance_from_home", "work_life_balance",
            "company_size", "company_reputation", "job_satisfaction", "performance_rating",
            "employee_recognition", "leadership_opportunities", "innovation_opportunities",
        ]]
    ],
    description="Features for employee attrition prediction model",
)

# Print feature count
print(f"Total features: {len(employee_features.schema)}")