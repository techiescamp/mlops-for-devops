import pandas as pd
import joblib
from config.paths import MODEL_PATH


def test(input_data: dict):
    # Load model (wrapped: predict() returns probabilities)
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Convert input to DataFrame
    df_input = pd.DataFrame([input_data])

    # predict() returns [[p_stay, p_leave]]
    probability = model.predict(df_input)[0]
    p_stay = probability[0]
    p_leave = probability[1]

    prediction = 1 if p_leave >= 0.50 else 0
    print('prediction value: ', prediction)
    print("😢 Leave" if prediction == 1 else "😃 Stay")

    if p_leave >= 0.65:
        print(f'⏰ Risk: High ({p_leave:.4f})')
    elif p_leave >= 0.45:
        print(f'⏰ Risk: Medium ({p_leave:.4f})')
    elif p_leave >= 0.25:
        print(f'⏰ Risk: Low ({p_leave:.4f})')
    else:
        print(f'⏰ Risk: Very Low ({p_leave:.4f})')

    return probability, prediction


if __name__ == "__main__":
    print("=" * 60)
    print("Employee Attrition Prediction App")
    print("=" * 60)

    # Collect inputs
    print("Please Enter 'valid' values to get correct prediction:")
    print("-" * 60)

    years_at_company = float(input('Years at Company: '))
    performance_rating = float(input('Performance Rating (Low: 1, Below Avg: 2, Avg: 3, High: 4): '))
    no_of_promotions = int(input('Number of Promotions: '))
    overtime = int(input('Overtime (Low: 0, High: 1): '))
    edu_level = int(input('Education Level (School: 1, Bachelors-degree: 2, Master-degree: 3, Associate: 4, PhD: 5): '))
    no_of_dependents = int(input('Number of Dependents: '))
    job_level = int(input('Job Level (Entry: 1, Mid: 2, Senior: 3): '))
    company_size = int(input('Company Size (Small: 1, Medium: 2, Large: 3): '))
    company_tenure = float(input('Company Tenure: '))
    remote_work = int(input('Remote Work (No: 0, Yes: 1): '))
    company_reputation = float(input('Company Reputation (Poor: 1, Fair: 2, Good: 3, Excellent: 4): '))
    overall_satisfaction = float(input('Overall Satisfaction (Low: 1, Medium: 2, High: 3, Very High: 4): '))
    opportunities = float(input('Opportunities (Low: 1, Medium: 2, High: 3): '))
    annual_income = int(input('Annual Income (0: Under 2.4L, 1: 2.4L–4.2L, 2: 4.2L–6L, 3: 6L–20L, 4: Above 20L): '))
    age_group = int(input('Age Group (1: 18–25, 2: 25–35, 3: 35–45, 4: 45–60, 5: 60–65): '))

    # Derived features
    role_stagnation_ratio = round(years_at_company / (company_tenure + 1), 3)
    tenure_gap = round(company_tenure - years_at_company, 2)
    early_company_tenure_risk = 1 if years_at_company <= 2 else 0
    long_tenure_low_role_risk = 1 if (company_tenure > 5 and job_level <= 2) else 0

    # Build input dictionary
    input_record = {
        "Years at Company": years_at_company,
        "Performance Rating": performance_rating,
        "Number of Promotions": no_of_promotions,
        "Overtime": overtime,
        "Education Level": edu_level,
        "Number of Dependents": no_of_dependents,
        "Job Level": job_level,
        "Company Size": company_size,
        "Company Tenure": company_tenure,
        "Remote Work": remote_work,
        "Company Reputation": company_reputation,
        "OverallSatisfaction": overall_satisfaction,
        "Opportunities": opportunities,
        "AnnualIncome": annual_income,
        "AgeGroup": age_group,
        "RoleStagnationRatio": role_stagnation_ratio,
        "TenureGap": tenure_gap,
        "EarlyCompanyTenureRisk": early_company_tenure_risk,
        "LongTenureLowRoleRisk": long_tenure_low_role_risk
    }

    # Run test
    test(input_record)
