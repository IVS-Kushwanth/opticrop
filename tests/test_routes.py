"""Tests for OptiCrop Flask routes."""
import json

import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models.user import User


@pytest.fixture
def app():
    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client, app):
    with app.app_context():
        user = User(name='Route Tester', email='routes@opticrop.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()

    client.post('/login', data={
        'email': 'routes@opticrop.com',
        'password': 'testpass',
    })
    return client


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'OptiCrop' in response.data
    assert b'Grow Smarter' in response.data


def test_predict_form_get(client):
    response = client.get('/predict')
    assert response.status_code == 200
    assert b'Find Your Optimal Crop' in response.data
    assert b'nitrogen' in response.data


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Welcome Back' in response.data


def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create Account' in response.data


def test_register_and_login(client, app):
    response = client.post('/register', data={
        'name': 'New User',
        'email': 'new@opticrop.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'role': 'farmer',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful' in response.data or b'Welcome Back' in response.data

    response = client.post('/login', data={
        'email': 'new@opticrop.com',
        'password': 'password123',
    }, follow_redirects=True)
    assert response.status_code == 200


def test_dashboard_page(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_analytics_page(client):
    response = client.get('/analytics')
    assert response.status_code == 200
    assert b'Analytics' in response.data


def test_history_page(client):
    response = client.get('/history')
    assert response.status_code == 200


def test_compare_page(client):
    response = client.get('/compare')
    assert response.status_code == 200
    assert b'Compare All ML Models' in response.data


def test_api_index(client):
    response = client.get('/api/v1/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'OptiCrop API'
    assert 'predict' in data['endpoints']


def test_api_stats(client):
    response = client.get('/api/v1/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'model_accuracies' in data
    assert 'crop_distribution' in data
    assert 'prediction_timeline' in data


def test_api_predict_missing_body(client):
    response = client.post('/api/v1/predict', content_type='application/json')
    assert response.status_code == 400


def test_api_predict_invalid_input(client):
    response = client.post('/api/v1/predict',
                           json={'nitrogen': -5},
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'errors' in data


def test_404_page(client):
    response = client.get('/nonexistent-page-xyz')
    assert response.status_code == 404
    assert b'404' in response.data


def test_logout(auth_client):
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200


def test_predict_post_invalid(client):
    response = client.post('/predict', data={
        'nitrogen': 'invalid',
        'phosphorous': 42,
        'potassium': 43,
        'temperature': 25,
        'humidity': 80,
        'ph': 6.5,
        'rainfall': 200,
        'algorithm': 'random_forest',
    })
    assert response.status_code == 200
    assert b'must be a valid number' in response.data or b'danger' in response.data
