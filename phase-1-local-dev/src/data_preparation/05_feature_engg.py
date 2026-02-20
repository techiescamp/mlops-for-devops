# | Column               | Meaning                                | Evidence                       |
# | -------------------- | -------------------------------------- | ------------------------------ |
# | **Years at Company** | Years in the *current role / position* | Usually smaller, role-specific |
# | **Company Tenure**   | Total years employed at the company    | Usually ≥ Years at Company     |


import pandas as pd
from config.paths import CLEANING_PATH, FEATURED_PATH

def feature_data(df):
    df_fe = df.copy()

    # Encoding
    # ------------------------------------
    # 1. Target column
    df_fe['Attrition'] = df_fe['Attrition'].map({'Stayed': 0, 'Left': 1}).astype('int')


    # 2. Binary Encoding
    binary_cols = ["Remote Work", "Leadership Opportunities", "Innovation Opportunities", "Overtime"]
    for col in binary_cols:
        df_fe[col] = df_fe[col].map({"Yes": 1, "No": 0}).astype("Int64")


    # ordinal encoding for features
    ordinal_maps = {
        "Work-Life Balance": { "Poor": 1, "Fair": 2, "Good": 3, "Excellent": 4 },
        "Job Satisfaction": { "Low": 1, "Medium": 2, "High": 3, "Very High": 4 },
        "Performance Rating": { "Low": 1, "Below Average": 2, "Average": 3, "High": 4 },
        "Employee Recognition": { "Low": 1, "Medium": 2, "High": 3, "Very High": 4 },
        "Company Reputation": { "Poor": 1, "Fair": 2, "Good": 3, "Excellent": 4 },
        "Job Level": { "Entry": 1, "Mid": 2, "Senior": 3},
        "Company Size": { "Small": 1, "Medium": 2, "Large": 3 },
        "Education Level": {"High School": 1, "Bachelor’s Degree": 2, "Master’s Degree": 3, "Associate Degree": 4, "PhD": 5},
    }

    for col, mapping in ordinal_maps.items():
        df_fe[col] = df_fe[col].map(mapping)


    # Aggregate satisfaction
    df_fe["OverallSatisfaction"] = ((df_fe["Work-Life Balance"] + df_fe["Job Satisfaction"] + df_fe["Employee Recognition"]) / 3).round().astype("Int64")
    df_fe = df_fe.drop(columns=["Work-Life Balance", "Job Satisfaction", "Employee Recognition"])


    df_fe['Opportunities'] = df_fe['Leadership Opportunities'] + df_fe['Innovation Opportunities']
    df_fe = df_fe.drop(columns=['Leadership Opportunities', 'Innovation Opportunities'])


    # annual income binning
    df_fe["AnnualIncome"] = df_fe["Monthly Income"] * 12

    df_fe["AnnualIncome"] = pd.cut(
        df_fe["AnnualIncome"],
        bins=[0, 240000, 420000, 600000, 2000000, float("inf")],
        labels=[0, 1, 2, 3, 4],
        include_lowest=True
    ).astype("Int64")
    df_fe = df_fe.drop(columns=["Monthly Income"])


    # age binning
    df_fe['AgeGroup'] = pd.cut(
        df_fe['Age'], 
        bins=[17, 25, 35, 45, 60, 65], 
        labels=[1, 2, 3, 4, 5]
    ).astype("Int64")
    df_fe = df_fe.drop(columns=['Age'])

    # Years At Company and Company Tenure 
    # 1. Convert to proper years as dataset is in months.
    df_fe["Years at Company"] = (df_fe["Years at Company"] / 12).round(2)
    df_fe["Company Tenure"] = (df_fe["Company Tenure"] / 12).round(2)

    # 2. Role Stagnation: 1 -> same role entire tenure (possible stagnation); low value -> role mobility
    df_fe['RoleStagnationRatio'] = ( df_fe['Years at Company'] / (df_fe['Company Tenure'] + 1) ).round(3)

    # 3. Tenure Gap: high gap -> role changes/promotion; low gap -> same role for long time
    df_fe['TenureGap'] = df_fe['Company Tenure'] - df_fe['Years at Company']

    # 4. Early Comapny risk: most attrition happens in first 2 years
    df_fe['EarlyCompanyTenureRisk'] = (df_fe['Years at Company'] <= 2).astype("Int64")

    # 5. Long Term Stagnation
    df_fe["LongTenureLowRoleRisk"] = ( (df_fe["Company Tenure"] > 5) & (df_fe["Job Level"] <= 2) ).astype("Int64")


    # drop unnecessary columns
    df_fe = df_fe.drop(columns=['Employee ID', 'Job Role', 'Distance from Home', 'Marital Status', 'Gender', 'dataset_type'])

    print(df_fe.tail(10))

    df_fe.to_csv(FEATURED_PATH, index=False)

    return df_fe


if __name__ == "__main__":
    df = pd.read_csv(CLEANING_PATH)
    feature_data(df)