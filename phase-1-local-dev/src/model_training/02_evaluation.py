import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score, roc_auc_score
from config.paths import PREPROCESSED_TRAIN_PATH, PREPROCESSED_TEST_PATH, MODEL_PATH, ARTIFACT_DIR


def get_feature_names(pipeline, original_columns):
    """Extract feature names in the order ColumnTransformer outputs them."""
    ct = pipeline.named_steps['preprocessor']
    feature_names = []
    for name, transformer, indices in ct.transformers_:
        if name == 'remainder':
            feature_names.extend([original_columns[i] for i in indices])
        else:
            feature_names.extend([original_columns[i] for i in indices])
    return feature_names


def evaluate_data(X_train, y_train, X_test, y_test):
    # load pipeline
    pipeline = joblib.load(MODEL_PATH)

    y_pred = pipeline.predict(X_test)

    # metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    class_report = classification_report(y_test, y_pred)
    print("Evaluation Metrics:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"ROC-AUC:  {roc_auc:.4f}")
    print("Confusion Matrix:")
    print(conf_matrix)
    print("Classification Report:")
    print(class_report)

    # train/test scores
    train_score = pipeline.score(X_train, y_train)
    test_score = pipeline.score(X_test, y_test)

    print('train score %: ', train_score * 100)
    print('test score %: ', test_score * 100)

    # feature importance
    feature_names = get_feature_names(pipeline, X_train.columns.tolist())
    coef = pipeline.named_steps['classifier'].coef_[0]
    coef_df = pd.DataFrame({'Feature': feature_names, 'Coefficient': coef})
    coef_df['Abs_Coefficient'] = np.abs(coef_df['Coefficient'])
    coef_df = coef_df.sort_values(by='Abs_Coefficient', ascending=False)
    print(coef_df)

    plt.figure(figsize=(10,6))
    plt.barh(coef_df['Feature'], coef_df['Coefficient'])
    plt.gca().invert_yaxis()
    plt.xlabel("Coefficient")
    plt.title("Logistic Regression Feature Importance")
    plt.tight_layout()

    return recall



if __name__ == "__main__":
    df_train = pd.read_csv(PREPROCESSED_TRAIN_PATH)
    df_test = pd.read_csv(PREPROCESSED_TEST_PATH)

    X_train = df_train.drop(columns=['Attrition'])
    y_train = df_train['Attrition']

    X_test = df_test.drop(columns=['Attrition'])
    y_test = df_test['Attrition']

    evaluate_data(X_train, y_train, X_test, y_test)
