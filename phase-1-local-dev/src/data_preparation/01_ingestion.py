import pandas as pd
from pandas import DataFrame
from config.paths import RAW_DATA_PATH, INGESTION_PATH


def ingestion() -> DataFrame:
    df = pd.read_csv(RAW_DATA_PATH)
    print(df.head(5))
    print("------")

    print(f"Shape: {df.shape}")
    print("------")

    print(f"Information: {df.info()}")
    print("------")
    
    df.to_csv(INGESTION_PATH, index=False)
    return df


if __name__ == "__main__":
    ingestion()