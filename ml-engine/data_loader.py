"""
cd
This module strictly handles data ingestion and preprocessing. It separates 
the data manipulation logic from the actual model training loop. It converts 
timestamps into cyclical numerical features (hour of day) and encodes 
categorical strings (IPs, resources, entity IDs) into mathematical representations 
suitable for Autoencoders or One-Class SVMs.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

class AccessLogPreprocessor:
    def __init__(self): 
        self.encoders = {
            'entity_id': LabelEncoder(),
            'source_ip': LabelEncoder(),
            'resource_accessed': LabelEncoder(),
            'auth_method': LabelEncoder(),
            'device_fingerprint': LabelEncoder()
        } 
        self.scaler = StandardScaler()
        
    def load_and_preprocess(self, csv_path, is_training=True):
        print(f"Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
 
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour_of_day'] = df['timestamp'].dt.hour
         
        categorical_columns = ['entity_id', 'source_ip', 'resource_accessed', 'auth_method', 'device_fingerprint']
        
        for col in categorical_columns:
            if is_training: 
                df[col + '_encoded'] = self.encoders[col].fit_transform(df[col])
            else:
                
                df[col + '_encoded'] = self.encoders[col].transform(df[col])

        # 3. Scale Numerical Variables
        numerical_features = ['session_duration', 'hour_of_day']
        if is_training:
            df[numerical_features] = self.scaler.fit_transform(df[numerical_features])
        else:
            df[numerical_features] = self.scaler.transform(df[numerical_features])
 
        feature_cols = [
            'entity_id_encoded', 'source_ip_encoded', 'resource_accessed_encoded',
            'auth_method_encoded', 'device_fingerprint_encoded', 
            'session_duration', 'hour_of_day'
        ]
        
        X = df[feature_cols].values
        
        # Keep labels separate for evaluation
        y = df['label'].values
        
        return X, y, df

    def save_preprocessors(self, output_dir="saved_models"):
        """Saves the encoders and scalers so the API can use them during real-time inference."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        joblib.dump(self.encoders, os.path.join(output_dir, 'encoders.joblib'))
        joblib.dump(self.scaler, os.path.join(output_dir, 'scaler.joblib'))
        print(f"Preprocessors successfully saved to {output_dir}/")

 
if __name__ == "__main__":
    # Go up one directory to find the synthetic-data exports
    data_path = "../synthetic-data/exports/final_training_dataset.csv"
    
    preprocessor = AccessLogPreprocessor()
    X, y, original_df = preprocessor.load_and_preprocess(data_path, is_training=True)
    
    print("\n--- Data Preprocessing Complete ---")
    print(f"Shape of numerical feature matrix (X): {X.shape}")
    print(f"First row of processed numerical data:\n{X[0]}")
    print(f"Target label for first row: {y[0]}")
    
    # Save the preprocessors for future use
    preprocessor.save_preprocessors()