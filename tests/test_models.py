"""Tests for OptiCrop database models."""
import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models.prediction import Prediction
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


def test_user_creation(app):
    with app.app_context():
        user = User(name='Test Farmer', email='test@opticrop.com', role='farmer')
        user.set_password('secret123')
        db.session.add(user)
        db.session.commit()

        fetched = User.query.filter_by(email='test@opticrop.com').first()
        assert fetched is not None
        assert fetched.name == 'Test Farmer'
        assert fetched.role == 'farmer'
        assert fetched.check_password('secret123')
        assert not fetched.check_password('wrong')


def test_user_password_hash_not_plaintext(app):
    with app.app_context():
        user = User(name='Secure User', email='secure@opticrop.com')
        user.set_password('mypassword')
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != 'mypassword'
        assert len(user.password_hash) > 20


def test_prediction_creation(app):
    with app.app_context():
        user = User(name='Predictor', email='pred@opticrop.com')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()

        pred = Prediction(
            user_id=user.id,
            nitrogen=90.0,
            phosphorous=42.0,
            potassium=43.0,
            temperature=25.0,
            humidity=80.0,
            ph=6.5,
            rainfall=200.0,
            algorithm='random_forest',
            predicted_crop='rice',
            confidence=0.95,
            all_probabilities='{"rice": 0.95}',
        )
        db.session.add(pred)
        db.session.commit()

        saved = Prediction.query.first()
        assert saved.predicted_crop == 'rice'
        assert saved.confidence == 0.95
        assert saved.user_id == user.id
        assert saved.nitrogen == 90.0


def test_user_prediction_relationship(app):
    with app.app_context():
        user = User(name='Farmer', email='farmer@opticrop.com')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()

        for i in range(3):
            db.session.add(Prediction(
                user_id=user.id,
                nitrogen=90, phosphorous=42, potassium=43,
                temperature=25, humidity=80, ph=6.5, rainfall=200,
                algorithm='knn', predicted_crop='rice', confidence=0.9,
            ))
        db.session.commit()

        assert len(user.predictions) == 3


def test_user_unique_email(app):
    with app.app_context():
        user1 = User(name='User One', email='dup@opticrop.com')
        user1.set_password('pass')
        db.session.add(user1)
        db.session.commit()

        user2 = User(name='User Two', email='dup@opticrop.com')
        user2.set_password('pass')
        db.session.add(user2)
        with pytest.raises(Exception):
            db.session.commit()
