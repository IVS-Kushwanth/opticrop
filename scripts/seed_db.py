"""Seed database with sample users and predictions."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.prediction import Prediction
from app.models.crop_data import CropData
from app.ml.preprocessor import CropPreprocessor


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email='farmer@opticrop.demo').first():
            user = User(name='Demo Farmer', email='farmer@opticrop.demo', role='farmer')
            user.set_password('demo123')
            db.session.add(user)
            db.session.commit()
            print('Created demo user: farmer@opticrop.demo / demo123')

        user = User.query.filter_by(email='farmer@opticrop.demo').first()
        if Prediction.query.count() == 0:
            samples = [
                (90, 42, 43, 20.9, 82, 6.5, 202, 'random_forest', 'rice', 0.98),
                (77, 48, 20, 22.6, 65, 6.2, 82, 'knn', 'maize', 0.95),
                (101, 28, 29, 25.5, 58, 6.8, 158, 'random_forest', 'coffee', 0.97),
            ]
            for n, p, k, t, h, ph, r, algo, crop, conf in samples:
                pred = Prediction(
                    user_id=user.id if user else None,
                    nitrogen=n, phosphorous=p, potassium=k,
                    temperature=t, humidity=h, ph=ph, rainfall=r,
                    algorithm=algo, predicted_crop=crop, confidence=conf,
                    all_probabilities=json.dumps({crop: conf}),
                )
                db.session.add(pred)
            db.session.commit()
            print(f'Seeded {len(samples)} predictions')

        csv_path = 'data/Crop_recommendation.csv'
        if os.path.exists(csv_path) and CropData.query.count() == 0:
            preprocessor = CropPreprocessor()
            df = preprocessor.load_data(csv_path)
            for _, row in df.head(100).iterrows():
                db.session.add(CropData(
                    N=row['N'], P=row['P'], K=row['K'],
                    temperature=row['temperature'], humidity=row['humidity'],
                    ph=row['ph'], rainfall=row['rainfall'], label=row['label'],
                ))
            db.session.commit()
            print('Seeded crop_data table with 100 rows')


if __name__ == '__main__':
    seed()
