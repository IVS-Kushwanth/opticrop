import os
import pickle

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


class CropPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

    def load_data(self, filepath):
        df = pd.read_csv(filepath)
        if len(df.columns) == 8:
            df.columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']
        df.dropna(inplace=True)
        df = df[(df['N'] >= 0) & (df['P'] >= 0) & (df['K'] >= 0)]
        df['label'] = df['label'].astype(str).str.strip().str.lower()
        return df

    def prepare_features(self, df, fit=True):
        X = df[self.feature_columns].values
        y = df['label'].values
        if fit:
            X_scaled = self.scaler.fit_transform(X)
            y_encoded = self.label_encoder.fit_transform(y)
        else:
            X_scaled = self.scaler.transform(X)
            y_encoded = self.label_encoder.transform(y)
        return X_scaled, y_encoded

    def split_data(self, X, y, test_size=0.2, random_state=42):
        _, class_counts = np.unique(y, return_counts=True)
        n_classes = len(class_counts)
        n_samples = len(y)
        n_test = int(np.ceil(n_samples * test_size)) if isinstance(test_size, float) else int(test_size)
        n_train = n_samples - n_test
        can_stratify = (
            n_classes > 1
            and class_counts.min() >= 2
            and n_train >= n_classes
            and n_test >= n_classes
        )
        stratify = y if can_stratify else None
        return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=stratify)

    def preprocess_single_input(self, n, p, k, temp, humidity, ph, rainfall):
        input_array = np.array([[n, p, k, temp, humidity, ph, rainfall]])
        return self.scaler.transform(input_array)

    def save(self, path='models/scaler.pkl'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({'scaler': self.scaler, 'label_encoder': self.label_encoder}, f)

    def load(self, path='models/scaler.pkl'):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.scaler = data['scaler']
            self.label_encoder = data['label_encoder']
