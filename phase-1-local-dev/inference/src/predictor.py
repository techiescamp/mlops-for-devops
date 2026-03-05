import joblib
from pathlib import Path

FEATURE_ORDER = [
    "Years at Company", "Performance Rating", "Number of Promotions",
    "Overtime", "Education Level", "Number of Dependents",
    "Job Level", "Company Size", "Company Tenure", "Remote Work",
    "Company Reputation", "OverallSatisfaction", "Opportunities",
    "AnnualIncome", "AgeGroup", "RoleStagnationRatio", "TenureGap",
    "EarlyCompanyTenureRisk", "LongTenureLowRoleRisk"
]

THRESHOLD = 0.50


class Predictor:
    def __init__(self):
        model_path = Path("artifacts/model.pkl")
        obj = joblib.load(model_path)
        self.predict_fn = obj.predict  # bound method — not the full sklearn object

    def is_loaded(self) -> bool:
        return self.predict_fn is not None

    def predict(self, features: dict) -> dict:
        values  = [[features[k] for k in FEATURE_ORDER]]
        probs   = self.predict_fn(values)[0]
        p_stay  = float(probs[0])
        p_leave = float(probs[1])

        return {
            "prediction": int(p_leave >= THRESHOLD),
            "p_leave":    round(p_leave, 4),
            "p_stay":     round(p_stay, 4),
            "risk":       self._tier(p_leave),
            "threshold":  THRESHOLD,
        }

    def _tier(self, prob: float) -> str:
        if prob >= 0.65: return "HIGH"
        if prob >= 0.45: return "MEDIUM"
        if prob >= 0.25: return "LOW"
        return "VERY_LOW"