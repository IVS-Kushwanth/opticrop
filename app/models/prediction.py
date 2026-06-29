from datetime import datetime

from app.extensions import db


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    nitrogen = db.Column(db.Float)
    phosphorous = db.Column(db.Float)
    potassium = db.Column(db.Float)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    ph = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    algorithm = db.Column(db.String(50))
    predicted_crop = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    all_probabilities = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
