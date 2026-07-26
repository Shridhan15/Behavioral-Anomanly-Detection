"""

This script implements a One-Class Support Vector Machine (SVM) to represent 
per-entity "normal" behavior, fulfilling Deliverable 2. 
Crucially, the model is trained EXCLUSIVELY on the 'normal' baseline data. 
It learns to draw a tight decision boundary around habitual patterns. 
During evaluation, it is exposed to the full dataset (including injected attacks). 
Any data point falling outside the learned boundary is flagged as an anomaly (-1).
"""

import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.metrics import classification_report, confusion_matrix
from data_loader import AccessLogPreprocessor
import joblib
import os

def train_and_evaluate_baseline(): 
    print("Loading data via preprocessor.")
    data_path = "../synthetic-data/exports/final_training_dataset.csv"
    preprocessor = AccessLogPreprocessor()
    X, y, df_original = preprocessor.load_and_preprocess(data_path, is_training=True)
 
    print("Isolating normal baseline for training...")
    normal_indices = np.where(y == 'normal')[0]
    X_train_normal = X[normal_indices]

    
    print(f"Training One-Class SVM on {len(X_train_normal)} normal logs...")
    baseline_model = OneClassSVM(kernel='rbf', gamma='scale', nu=0.01)
    baseline_model.fit(X_train_normal)
 
    print("Evaluating model against full dataset (including injected attacks)...")
    
    # The model outputs 1 for inliers (normal) and -1 for outliers (anomalies)
    predictions = baseline_model.predict(X)
 
    # 'normal' becomes 1, everything else (brute_force, lateral_movement, etc.) becomes -1
    y_true_binary = np.where(y == 'normal', 1, -1)

    #  Output Metrics
    print("\n--- BASELINE MODEL EVALUATION ---")
    print("Confusion Matrix:") 
    print(confusion_matrix(y_true_binary, predictions))
    
    print("\nClassification Report:")
    # Map back to readable names for the terminal
    target_names = ['Anomaly (-1)', 'Normal (1)']
    print(classification_report(y_true_binary, predictions, target_names=target_names))

    # Save the trained model
    output_dir = "saved_models"
    model_path = os.path.join(output_dir, 'one_class_svm.joblib')
    joblib.dump(baseline_model, model_path)
    print(f"\nModel successfully saved to {model_path}")

if __name__ == "__main__":
    train_and_evaluate_baseline()