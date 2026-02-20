import pandas as pd
from config.paths import EDA_PATH, CLEANING_PATH

def clean_data(df):
    print("--- Find duplicates ---")
    df_duplicate = df.duplicated()
    print(f"Number of duplicate rows: {df_duplicate.sum()}")

    print("--- Find Missing/Null values ---")
    missing_values = df.isnull().sum()
    print(f"Missing values: {missing_values}")

    df.to_csv(CLEANING_PATH, index=False)

    return df

if __name__ == "__main__":
    df = pd.read_csv(EDA_PATH)
    clean_data(df)
