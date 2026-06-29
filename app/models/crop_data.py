from app.extensions import db


class CropData(db.Model):
    __tablename__ = 'crop_data'

    id = db.Column(db.Integer, primary_key=True)
    N = db.Column(db.Float, nullable=False)
    P = db.Column(db.Float, nullable=False)
    K = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    label = db.Column(db.String(100), nullable=False)
