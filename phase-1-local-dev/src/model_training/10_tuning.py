import json
import types
import pandas as pd
import joblib
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
from config.paths import PREPROCESSED_TRAIN_PATH, PREPROCESSED_TEST_PATH, MODEL_PATH, METRICS_PATH


def tuning_data(X_train, y_train, X_test, y_test):

    # load pipeline
    pipeline = joblib.load(MODEL_PATH)

    # set parameters (classifier__ prefix for Pipeline)
    param_grid = {
        'classifier__C': [0.01, 0.1, 1, 10, 100],
        'classifier__solver': ['liblinear', 'saga'],
        'classifier__max_iter': [1000]
    }

    # set cv
    strat_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # use gridsearchcv for tuning model
    grid = GridSearchCV(pipeline, param_grid=param_grid, cv=strat_cv, scoring='recall')

    # train gridsearchcv model
    grid.fit(X_train, y_train)

    # get best model and save
    tuned_pipeline = grid.best_estimator_
    joblib.dump(tuned_pipeline, MODEL_PATH)

    print(f'best params: {grid.best_params_}')
    print(f'best cv scores: {grid.best_score_ * 100}')
    print(f'best model: {tuned_pipeline}')

    # log cv results
    results = pd.DataFrame(grid.cv_results_)
    print(results.head(3))

    # predict the output with tuned pipeline
    y_pred_ht = tuned_pipeline.predict(X_test)

    # tuned model evaluation
    accuracy_ht = accuracy_score(y_test, y_pred_ht)
    recall_ht = recall_score(y_test, y_pred_ht)
    print('accuracy: ', accuracy_ht)
    print('recall: ', recall_ht)

    # get train/test score
    tuned_train_score = tuned_pipeline.score(X_train, y_train)
    tuned_test_score = tuned_pipeline.score(X_test, y_test)

    print('tuned train score: ', tuned_train_score)
    print('tuned test score: ', tuned_test_score)

    # Compare CV scores of base model and tuned model
    base_cv_scores = cross_val_score(pipeline, X_train, y_train, cv=strat_cv)
    tuned_cv_scores = cross_val_score(tuned_pipeline, X_train, y_train, cv=strat_cv)

    print("=== MODEL COMPARISON ===")
    print(f"Base Model CV:     {base_cv_scores.mean():.4f} (+/- {base_cv_scores.std():.4f})")
    print(f"Tuned Model CV:    {tuned_cv_scores.mean():.4f} (+/- {tuned_cv_scores.std():.4f})")

    metrics = {
        "accuracy": accuracy_ht,
        "recall": recall_ht
    }
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)

    # Patch for KServe sklearn 1.5.2 (multi_class removed in 1.6+)
    tuned_pipeline.named_steps['classifier'].multi_class = 'auto'

    # Wrap so predict() returns probabilities for KServe
    # Uses SimpleNamespace + bound method - no custom classes needed
    wrapped = types.SimpleNamespace(predict=tuned_pipeline.predict_proba)
    joblib.dump(wrapped, MODEL_PATH)

    return metrics


if __name__ == "__main__":
    df_train = pd.read_csv(PREPROCESSED_TRAIN_PATH)
    df_test = pd.read_csv(PREPROCESSED_TEST_PATH)

    X_train = df_train.drop(columns=['Attrition'])
    y_train = df_train['Attrition']

    X_test = df_test.drop(columns=['Attrition'])
    y_test = df_test['Attrition']

    tuning_data(X_train, y_train, X_test, y_test)
