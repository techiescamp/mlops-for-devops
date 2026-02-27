import pandas as pd
import joblib
from sklearn.model_selection import cross_val_score, StratifiedKFold
from config.paths import PREPROCESSED_TRAIN_PATH, MODEL_PATH


def cv_data(X_train, y_train):

    pipeline = joblib.load(MODEL_PATH)

    strat_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=strat_cv, scoring='recall')

    print(f"Strat cv score: {cv_scores.mean() * 100}")
    return cv_scores



if __name__ == "__main__":
    df_train = pd.read_csv(PREPROCESSED_TRAIN_PATH)

    X_train = df_train.drop(columns=['Attrition'])
    y_train = df_train['Attrition']

    cv_data(X_train, y_train)
