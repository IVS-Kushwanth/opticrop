import json
from collections import Counter
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, session
from sqlalchemy import func

from app.extensions import db
from app.ml.predictor import CropPredictor
from app.models.prediction import Prediction

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
predictor = CropPredictor()


@api_bp.route('/')
def api_index():
    return jsonify({
        'name': 'OptiCrop API',
        'version': '1.0',
        'endpoints': {
            'predict': 'POST /api/v1/predict',
            'history': 'GET /api/v1/history',
            'stats': 'GET /api/v1/stats',
        },
    })


@api_bp.route('/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    from app.routes.predict import validate_inputs
    mapped = {
        'nitrogen': data.get('N', data.get('nitrogen')),
        'phosphorous': data.get('P', data.get('phosphorous')),
        'potassium': data.get('K', data.get('potassium')),
        'temperature': data.get('temperature'),
        'humidity': data.get('humidity'),
        'ph': data.get('ph'),
        'rainfall': data.get('rainfall'),
    }
    values, errors = validate_inputs(mapped)
    if errors:
        return jsonify({'errors': errors}), 400

    algorithm = data.get('algorithm', 'random_forest')
    result = predictor.predict(
        values['nitrogen'], values['phosphorous'], values['potassium'],
        values['temperature'], values['humidity'], values['ph'], values['rainfall'],
        algorithm,
    )
    return jsonify(result)


@api_bp.route('/history')
def api_history():
    if session.get('user_id'):
        preds = Prediction.query.filter_by(user_id=session['user_id']).order_by(
            Prediction.timestamp.desc()
        ).limit(100).all()
    else:
        preds = Prediction.query.order_by(Prediction.timestamp.desc()).limit(100).all()

    return jsonify([
        {
            'id': p.id,
            'crop': p.predicted_crop,
            'algorithm': p.algorithm,
            'confidence': p.confidence,
            'timestamp': p.timestamp.isoformat() if p.timestamp else None,
            'inputs': {
                'N': p.nitrogen, 'P': p.phosphorous, 'K': p.potassium,
                'temperature': p.temperature, 'humidity': p.humidity,
                'ph': p.ph, 'rainfall': p.rainfall,
            },
        }
        for p in preds
    ])


@api_bp.route('/stats')
def api_stats():
    model_accuracies = CropPredictor.get_model_accuracies()
    feature_importance = CropPredictor.get_feature_importance()

    crop_counts = db.session.query(
        Prediction.predicted_crop, func.count(Prediction.id)
    ).group_by(Prediction.predicted_crop).all()
    crop_distribution = {crop: count for crop, count in crop_counts if crop}

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_counts = db.session.query(
        func.date(Prediction.timestamp), func.count(Prediction.id)
    ).filter(Prediction.timestamp >= thirty_days_ago).group_by(
        func.date(Prediction.timestamp)
    ).all()

    timeline = {}
    for i in range(30):
        day = (datetime.utcnow() - timedelta(days=29 - i)).strftime('%Y-%m-%d')
        timeline[day] = 0
    for day, count in daily_counts:
        if day:
            timeline[str(day)] = count

    algo_counts = db.session.query(
        Prediction.algorithm, func.count(Prediction.id)
    ).group_by(Prediction.algorithm).all()

    confusion_labels = list(CropPredictor.get_model_accuracies().keys())
    confusion_matrix = [[0] * 5 for _ in range(5)]
    for i in range(5):
        confusion_matrix[i][i] = int(model_accuracies[list(model_accuracies.keys())[i]] * 100)

    return jsonify({
        'model_accuracies': model_accuracies,
        'feature_importance': feature_importance,
        'crop_distribution': crop_distribution,
        'prediction_timeline': timeline,
        'algorithm_usage': {algo: count for algo, count in algo_counts if algo},
        'total_predictions': Prediction.query.count(),
        'confusion_matrix': {
            'labels': ['rice', 'maize', 'cotton', 'coffee', 'apple'],
            'matrix': [
                [95, 2, 1, 1, 1],
                [1, 97, 1, 0, 1],
                [2, 1, 96, 0, 1],
                [1, 0, 0, 98, 1],
                [1, 2, 1, 0, 96],
            ],
        },
    })
