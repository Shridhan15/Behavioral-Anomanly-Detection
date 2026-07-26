"""
 
This  implements a Long Short-Term Memory (LSTM) neural network. 
Unlike the baseline SVM which looks at logs in isolation, this model extracts 
chronologicalsliding windows (sequences of 5 events) for every entity. 
It fulfills Deliverable 3 by understanding temporal context (e.g., detecting 
impossible travel or lateral movement over time) and Deliverable 4 by acting 
as a multi-class classifier to categorize the exact attack type.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import classification_report
from data_loader import AccessLogPreprocessor
import joblib
import os

# Set sequence length  
SEQUENCE_LENGTH = 5

def create_sequences(X, y, entity_ids, seq_length):
    """
    Groups data by entity_id and creates chronological sliding windows.
    Example: Logs [1, 2, 3, 4, 5] become one sequence to predict the label of log 5.
    """
    X_seq, y_seq = [], []
    
    # Get unique entities  
    unique_entities = np.unique(entity_ids)
    
    for entity in unique_entities:
        # Find all logs for this  entity
        entity_mask = (entity_ids == entity)
        X_entity = X[entity_mask]
        y_entity = y[entity_mask]
        
        # Slide a window across this entity 
        for i in range(len(X_entity) - seq_length):
            X_seq.append(X_entity[i : i + seq_length])
            y_seq.append(y_entity[i + seq_length])
            
    return np.array(X_seq), np.array(y_seq)

def train_sequence_model():
    print(" Loading and preprocessing data...")
    data_path = "../synthetic-data/exports/final_training_dataset.csv"
    preprocessor = AccessLogPreprocessor()
    X_raw, y_raw, df_original = preprocessor.load_and_preprocess(data_path, is_training=True)
     
    entity_ids = df_original['entity_id'].values
    
    # Encoding the string labels 
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_raw)
    
    print(f" Building chronological sequences (Length: {SEQUENCE_LENGTH})...")
    X_seq, y_seq = create_sequences(X_raw, y_encoded, entity_ids, SEQUENCE_LENGTH)
    
    #  One-Hot Encoding for the Neural Network
    num_classes = len(label_encoder.classes_)
    y_seq_categorical = to_categorical(y_seq, num_classes=num_classes)
    
    #   (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X_seq, y_seq_categorical, test_size=0.2, random_state=42, shuffle=True
    )
    
    print(f"   Training sequences: {len(X_train)} | Testing sequences: {len(X_test)}")
    
    print(" Compiling the LSTM Neural Network...") 
    num_features = X_train.shape[2] 
    
    model = Sequential([
        LSTM(64, input_shape=(SEQUENCE_LENGTH, num_features), return_sequences=False),
        Dropout(0.2),  
        Dense(32, activation='relu'),
        Dense(num_classes, activation='softmax')  
    ])
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    
    print(" Training the model...")
    #  small number of epochs (10) for  prototyping
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.1, verbose=1)
    
    print("\n Evaluating the Sequence Model...") 
    y_pred_probs = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred_probs, axis=1)
    y_true_classes = np.argmax(y_test, axis=1)
     
    target_names = label_encoder.classes_
    
    print("\nLSTM CLASSIFICATION REPORT")
    print(classification_report(y_true_classes, y_pred_classes, target_names=target_names, labels=np.arange(len(target_names)), zero_division=0))
    
    # Save the model and the label encoder
    output_dir = "saved_models"
    model_path = os.path.join(output_dir, 'lstm_sequence_model.h5')
    encoder_path = os.path.join(output_dir, 'label_encoder.joblib')
    
    model.save(model_path)
    joblib.dump(label_encoder, encoder_path)
    print(f"\nModel successfully saved to {model_path}")

if __name__ == "__main__":
    train_sequence_model()