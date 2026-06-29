"""Tests for OptiCrop ML components."""
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from app.ml.preprocessor import CropPreprocessor
from app.routes.predict import validate_inputs


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'N': [90, 85, 20],
        'P': [42, 58, 130],
        'K': [43, 41, 280],
        'temperature': [25, 28, 15],
        'humidity': [80, 65, 60],
        'ph': [6.5, 7.0, 6.5],
        'rainfall': [200, 120, 100],
        'label': ['rice', 'maize', 'apple'],
    })


def test_validate_inputs_valid():
    data = {
        'nitrogen': 90, 'phosphorous': 42, 'potassium': 43,
        'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200,
    }
    values, errors = validate_inputs(data)
    assert errors == []
    assert values['nitrogen'] == 90.0
    assert values['rainfall'] == 200.0


def test_validate_inputs_with_alt_keys():
    data = {'N': 90, 'P': 42, 'K': 43, 'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200}
    values, errors = validate_inputs(data)
    assert errors == []
    assert values['nitrogen'] == 90.0


def test_validate_inputs_out_of_range():
    data = {
        'nitrogen': 200, 'phosphorous': 42, 'potassium': 43,
        'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200,
    }
    values, errors = validate_inputs(data)
    assert len(errors) > 0
    assert any('nitrogen' in e for e in errors)


def test_validate_inputs_missing():
    values, errors = validate_inputs({})
    assert len(errors) == 7


def test_validate_inputs_invalid_type():
    data = {
        'nitrogen': 'abc', 'phosphorous': 42, 'potassium': 43,
        'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200,
    }
    values, errors = validate_inputs(data)
    assert any('nitrogen' in e for e in errors)


def test_preprocessor_prepare_features(sample_df):
    preprocessor = CropPreprocessor()
    X, y = preprocessor.prepare_features(sample_df, fit=True)
    assert X.shape == (3, 7)
    assert len(y) == 3
    assert preprocessor.label_encoder.classes_.tolist() == ['apple', 'maize', 'rice']


def test_preprocessor_split_data(sample_df):
    preprocessor = CropPreprocessor()
    X, y = preprocessor.prepare_features(sample_df, fit=True)
    X_train, X_test, y_train, y_test = preprocessor.split_data(X, y, test_size=0.33)
    assert len(X_train) + len(X_test) == 3
    assert len(y_train) + len(y_test) == 3


def test_preprocessor_single_input(sample_df):
    preprocessor = CropPreprocessor()
    preprocessor.prepare_features(sample_df, fit=True)
    scaled = preprocessor.preprocess_single_input(90, 42, 43, 25, 80, 6.5, 200)
    assert scaled.shape == (1, 7)


def test_preprocessor_save_and_load(sample_df):
    preprocessor = CropPreprocessor()
    preprocessor.prepare_features(sample_df, fit=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, 'scaler.pkl')
        preprocessor.save(path)

        loaded = CropPreprocessor()
        loaded.load(path)
        scaled = loaded.preprocess_single_input(90, 42, 43, 25, 80, 6.5, 200)
        assert scaled.shape == (1, 7)


def test_crop_predictor_accuracies():
    from app.ml.predictor import CropPredictor
    accuracies = CropPredictor.get_model_accuracies()
    assert 'Random Forest' in accuracies
    assert accuracies['Random Forest'] == 0.99
    assert all(0 < v <= 1 for v in accuracies.values())
