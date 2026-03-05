from pydantic import BaseModel, Field


class EmployeeFeatures(BaseModel):
    years_at_company:     float = Field(..., example=3.0)
    performance_rating:   float = Field(..., example=3.0,  description="1=Low, 2=Below Avg, 3=Avg, 4=High")
    no_of_promotions:     int   = Field(..., example=1)
    overtime:             int   = Field(..., example=0,    description="0=Low, 1=High")
    edu_level:            int   = Field(..., example=2,    description="1=School, 2=Bachelors, 3=Masters, 4=Associate, 5=PhD")
    no_of_dependents:     int   = Field(..., example=0)
    job_level:            int   = Field(..., example=2,    description="1=Entry, 2=Mid, 3=Senior")
    company_size:         int   = Field(..., example=2,    description="1=Small, 2=Medium, 3=Large")
    company_tenure:       float = Field(..., example=5.0)
    remote_work:          int   = Field(..., example=0,    description="0=No, 1=Yes")
    company_reputation:   float = Field(..., example=3.0,  description="1=Poor, 2=Fair, 3=Good, 4=Excellent")
    overall_satisfaction: float = Field(..., example=3.0,  description="1=Low, 2=Medium, 3=High, 4=Very High")
    opportunities:        float = Field(..., example=2.0,  description="1=Low, 2=Medium, 3=High")
    annual_income:        int   = Field(..., example=2,    description="0=Under 2.4L, 1=2.4-4.2L, 2=4.2-6L, 3=6-20L, 4=Above 20L")
    age_group:            int   = Field(..., example=2,    description="1=18-25, 2=25-35, 3=35-45, 4=45-60, 5=60-65")

    def to_model_input(self) -> dict:
        """Compute derived features and return the full ordered record."""
        yac = self.years_at_company
        ct  = self.company_tenure
        jl  = self.job_level

        return {
            "Years at Company":        yac,
            "Performance Rating":      self.performance_rating,
            "Number of Promotions":    self.no_of_promotions,
            "Overtime":                self.overtime,
            "Education Level":         self.edu_level,
            "Number of Dependents":    self.no_of_dependents,
            "Job Level":               jl,
            "Company Size":            self.company_size,
            "Company Tenure":          ct,
            "Remote Work":             self.remote_work,
            "Company Reputation":      self.company_reputation,
            "OverallSatisfaction":     self.overall_satisfaction,
            "Opportunities":           self.opportunities,
            "AnnualIncome":            self.annual_income,
            "AgeGroup":                self.age_group,
            "RoleStagnationRatio":     round(yac / (ct + 1), 3),
            "TenureGap":               round(ct - yac, 2),
            "EarlyCompanyTenureRisk":  1 if yac <= 2 else 0,
            "LongTenureLowRoleRisk":   1 if (ct > 5 and jl <= 2) else 0,
        }


class PredictionResponse(BaseModel):
    prediction: int   = Field(..., example=1,       description="0=Stay, 1=Leave")
    p_leave:    float = Field(..., example=0.73)
    p_stay:     float = Field(..., example=0.27)
    risk:       str   = Field(..., example="HIGH",   description="VERY_LOW / LOW / MEDIUM / HIGH")
    threshold:  float = Field(..., example=0.50)