"""
Run: python scripts/train_models.py
Trains all 5 ML models and saves them as .pkl files in /models/
"""
import os
import sys
import urllib.request

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ml.preprocessor import CropPreprocessor
from app.ml.algorithms.knn import KNNCropModel
from app.ml.algorithms.logistic import LogisticCropModel
from app.ml.algorithms.decision_tree import DecisionTreeCropModel
from app.ml.algorithms.random_forest import RandomForestCropModel
from app.ml.algorithms.kmeans import KMeansCropModel

DATA_PATH = 'data/Crop_recommendation.csv'
DATA_URL = (
    'https://raw.githubusercontent.com/Gladiator07/Harvestify/master/'
    'Data-processed/crop_recommendation.csv'
)


def ensure_dataset():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(DATA_PATH):
        print(f'Downloading dataset from {DATA_URL}...')
        urllib.request.urlretrieve(DATA_URL, DATA_PATH)
        print('Dataset downloaded.')


def main():
    ensure_dataset()
    os.makedirs('models', exist_ok=True)

    print('Loading and preprocessing data...')
    preprocessor = CropPreprocessor()
    df = preprocessor.load_data(DATA_PATH)
    X, y = preprocessor.prepare_features(df, fit=True)
    X_train, X_test, y_train, y_test = preprocessor.split_data(X, y)
    preprocessor.save()

    results = {}

    print('Training KNN...')
    knn = KNNCropModel(n_neighbors=5)
    knn.train(X_train, y_train)
    results['KNN'] = knn.evaluate(X_test, y_test)
    knn.save()

    print('Training Logistic Regression...')
    lr = LogisticCropModel()
    lr.train(X_train, y_train)
    results['Logistic Regression'] = lr.evaluate(X_test, y_test)
    lr.save()

    print('Training Decision Tree...')
    dt = DecisionTreeCropModel()
    dt.train(X_train, y_train)
    results['Decision Tree'] = dt.evaluate(X_test, y_test)
    dt.save()

    print('Training Random Forest (Best Model)...')
    rf = RandomForestCropModel()
    rf.train(X_train, y_train)
    results['Random Forest'] = rf.evaluate(X_test, y_test)
    rf.save()

    print('Training KMeans Clustering...')
    km = KMeansCropModel(n_clusters=22)
    km.train(X_train, y_train, preprocessor.label_encoder)
    km.save()

    print('\n' + '=' * 50)
    print('MODEL ACCURACY COMPARISON')
    print('=' * 50)
    for name, res in results.items():
        print(f"{name:25s}: {res['accuracy'] * 100:.2f}%")
    print('=' * 50)
    print('All models saved to /models/')


if __name__ == '__main__':
    main()
