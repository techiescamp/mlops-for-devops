import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from config.paths import VALIDATION_PATH, EDA_PATH

def eda_data(df):
    # Basic statistics
    print("Basic Statistics:")
    print(df.describe(include='all'))

    # Distribution of Age
    plt.figure(figsize=(8, 6))
    sns.histplot(df['Age'], bins=30, kde=True)
    plt.title('Age Distribution')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    plt.show()

    # Attrition count plot
    plt.figure(figsize=(6, 4))
    sns.countplot(x='Attrition', data=df)
    plt.title('Attrition Count')
    plt.xlabel('Attrition')
    plt.ylabel('Count')
    plt.show()

    # Monthly Income vs Job Level
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Job Level', y='Monthly Income', data=df)
    plt.title('Monthly Income by Job Level')
    plt.xlabel('Job Level')
    plt.ylabel('Monthly Income')
    plt.show()

    # Correlation heatmap
    plt.figure(figsize=(12, 10))
    corr = df.select_dtypes(include=['int64', 'float64']).corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm')
    plt.title('Correlation Heatmap')
    plt.show()

    df.to_csv(EDA_PATH, index=False)
    return df

if __name__ == "__main__":
    df = pd.read_csv(VALIDATION_PATH)
    eda_data(df)
