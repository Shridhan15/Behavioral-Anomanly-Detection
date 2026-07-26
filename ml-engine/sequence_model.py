"""
This implements a Bidirectional Long Short-Term Memory (Bi-LSTM) neural network. 
It extracts 9-feature chronological sliding windows (sequences of 5 events).
The architecture has been upgraded to read sequences in both directions for 
superior context awareness, and introduces time-delta feature engineering 
to explicitly catch automated scripts and rapid anomalies.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics import classification_report
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from data_loader import AccessLogPreprocessor
import joblib
import os
import ast

SEQUENCE_LENGTH = 5

def create_sequences(X, y, entity_ids, seq_length):
    X_seq, y_seq = [], []
    unique_entities = np.unique(entity_ids)
    
    for entity in unique_entities:
        entity_mask = (entity_ids == entity)
        X_entity = X[entity_mask]
        y_entity = y[entity_mask]
        
        for i in range(len(X_entity) - seq_length):
            X_seq.append(X_entity[i : i + seq_length])
            y_seq.append(y_entity[i + seq_length])
            
    return np.array(X_seq), np.array(y_seq)

def train_sequence_model():
    print(" Loading and preprocessing data...")
    data_path = "../synthetic-data/exports/final_training_dataset.csv"
    preprocessor = AccessLogPreprocessor()
    X_raw, y_raw, df_original = preprocessor.load_and_preprocess(data_path, is_training=True)
     
    # Ensure strict chronological order per entity for accurate time deltas
    df_original['timestamp'] = pd.to_datetime(df_original['timestamp'])
    df_original.sort_values(by=['entity_id', 'timestamp'], inplace=True)
    entity_ids = df_original['entity_id'].values

    # --- 8TH FEATURE: Failed Auth Count ---
    print(" Extracting 8th feature: failed_auth_count...")
    def extract_failed_auths(seq_val):
        try:
            seq_list = ast.literal_eval(seq_val)
            return sum(1 for cmd in seq_list if "FAILED" in str(cmd))
        except:
            return 0
            
    failed_counts = df_original['command_sequence'].apply(extract_failed_auths).values.reshape(-1, 1)
    scaler_fails = MinMaxScaler()
    failed_counts_scaled = scaler_fails.fit_transform(failed_counts)
    
    # --- 9TH FEATURE: Time Since Last Event ---
    print(" Extracting 9th feature: time_since_last_event...")
    df_original['time_since_last_event'] = df_original.groupby('entity_id')['timestamp'].diff().dt.total_seconds().fillna(0)
    time_deltas = df_original['time_since_last_event'].values.reshape(-1, 1)
    
    scaler_time = MinMaxScaler()
    time_deltas_scaled = scaler_time.fit_transform(time_deltas)

    # Append both new features to the matrix (Total Features = 9)
    X_raw = np.hstack((X_raw, failed_counts_scaled, time_deltas_scaled))
    # ----------------------------------
    
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_raw)
    
    print(f" Building chronological sequences (Length: {SEQUENCE_LENGTH})...")
    X_seq, y_seq = create_sequences(X_raw, y_encoded, entity_ids, SEQUENCE_LENGTH)
    
    num_classes = len(label_encoder.classes_)
    y_seq_categorical = to_categorical(y_seq, num_classes=num_classes)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_seq, y_seq_categorical, test_size=0.2, random_state=42, shuffle=True
    )
    
    print(f" Training sequences: {len(X_train)} | Testing sequences: {len(X_test)}")
    
    print(" Compiling the Bidirectional LSTM Neural Network...") 
    num_features = X_train.shape[2] 
    
    # UPGRADED ARCHITECTURE: Bidirectional Wrapper
    model = Sequential([
        Bidirectional(LSTM(64, return_sequences=False), input_shape=(SEQUENCE_LENGTH, num_features)),
        Dropout(0.3),  
        Dense(32, activation='relu'),
        Dense(num_classes, activation='softmax')  
    ])
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    early_stop = EarlyStopping(
        monitor='val_loss', 
        patience=4, 
        restore_best_weights=True
    )
    
    print(" Training the model on perfectly balanced dataset...")
    # NOTE: class_weight parameter removed for pure 50/50 data testing
    model.fit(
        X_train, y_train, 
        epochs=40, 
        batch_size=64, 
        validation_split=0.1, 
        callbacks=[early_stop], 
        verbose=1
    )
    
    print("\n Evaluating the Sequence Model...") 
    y_pred_probs = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred_probs, axis=1)
    y_true_classes = np.argmax(y_test, axis=1)
     
    target_names = label_encoder.classes_
    
    print("\nLSTM CLASSIFICATION REPORT")
    print(classification_report(y_true_classes, y_pred_classes, target_names=target_names, labels=np.arange(len(target_names)), zero_division=0))
    
    output_dir = "saved_models"
    os.makedirs(output_dir, exist_ok=True)
    model.save(os.path.join(output_dir, 'lstm_sequence_model.h5'))
    joblib.dump(label_encoder, os.path.join(output_dir, 'label_encoder.joblib'))
    joblib.dump(scaler_fails, os.path.join(output_dir, 'scaler_fails.joblib'))
    joblib.dump(scaler_time, os.path.join(output_dir, 'scaler_time.joblib')) # Save 9th feature scaler
    
    print(f"\nModel successfully saved to {output_dir}")

if __name__ == "__main__":
    train_sequence_model()