import json

from flask import Blueprint, jsonify, render_template, request, session

from app.extensions import db
from app.ml.predictor import CropPredictor
from app.models.prediction import Prediction

predict_bp = Blueprint('predict', __name__)
predictor = CropPredictor()

VALID_ALGORITHMS = {'knn', 'logistic', 'decision_tree', 'random_forest', 'kmeans'}


def validate_inputs(data):
    field_map = {
        'nitrogen': ('N', 0, 140),
        'phosphorous': ('P', 5, 145),
        'potassium': ('K', 5, 205),
        'temperature': ('temperature', 8, 44),
        'humidity': ('humidity', 14, 100),
        'ph': ('ph', 3.5, 9.5),
        'rainfall': ('rainfall', 20, 300),
    }
    errors = []
    values = {}
    for field, (alt_key, lo, hi) in field_map.items():
        raw = data.get(field, data.get(alt_key))
        try:
            val = float(raw)
            if val < lo or val > hi:
                errors.append(f'{field} must be between {lo} and {hi}')
            values[field] = val
        except (TypeError, ValueError):
            errors.append(f'{field} must be a valid number')
    return values, errors


@predict_bp.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return render_template('predict/form.html', model_error=CropPredictor.load_error)

    values, errors = validate_inputs(request.form)
    if errors:
        for err in errors:
            from flask import flash
            flash(err, 'danger')
        return render_template('predict/form.html', model_error=CropPredictor.load_error)

    algorithm = request.form.get('algorithm', 'random_forest')
    if algorithm not in VALID_ALGORITHMS:
        algorithm = 'random_forest'

    result = predictor.predict(
        values['nitrogen'], values['phosphorous'], values['potassium'],
        values['temperature'], values['humidity'], values['ph'], values['rainfall'],
        algorithm,
    )

    if 'error' not in result:
        pred = Prediction(
            user_id=session.get('user_id'),
            nitrogen=values['nitrogen'],
            phosphorous=values['phosphorous'],
            potassium=values['potassium'],
            temperature=values['temperature'],
            humidity=values['humidity'],
            ph=values['ph'],
            rainfall=values['rainfall'],
            algorithm=algorithm,
            predicted_crop=result['crop'],
            confidence=result.get('confidence') or 0,
            all_probabilities=json.dumps(result.get('probabilities', {})),
        )
        db.session.add(pred)
        db.session.commit()

    return render_template('predict/result.html', result=result, inputs=values)


@predict_bp.route('/predict/<algorithm>', methods=['POST'])
def predict_algorithm(algorithm):
    if algorithm not in VALID_ALGORITHMS:
        return jsonify({'error': 'Invalid algorithm'}), 400
    data = request.get_json() or request.form
    values, errors = validate_inputs(data)
    if errors:
        return jsonify({'errors': errors}), 400
    result = predictor.predict(
        values['nitrogen'], values['phosphorous'], values['potassium'],
        values['temperature'], values['humidity'], values['ph'], values['rainfall'],
        algorithm,
    )
    return jsonify(result)


@predict_bp.route('/compare', methods=['GET', 'POST'])
def compare_all():
    if request.method == 'GET':
        return render_template('predict/compare.html')

    data = request.get_json() or {}
    mapped = {
        'nitrogen': data.get('n', data.get('nitrogen')),
        'phosphorous': data.get('p', data.get('phosphorous')),
        'potassium': data.get('k', data.get('potassium')),
        'temperature': data.get('temperature'),
        'humidity': data.get('humidity'),
        'ph': data.get('ph'),
        'rainfall': data.get('rainfall'),
    }
    values, errors = validate_inputs(mapped)
    if errors:
        return jsonify({'errors': errors}), 400

    results = predictor.predict_all(
        values['nitrogen'], values['phosphorous'], values['potassium'],
        values['temperature'], values['humidity'], values['ph'], values['rainfall'],
    )
    return jsonify(results)


@predict_bp.route('/history')
def history():
    if session.get('user_id'):
        preds = Prediction.query.filter_by(user_id=session['user_id']).order_by(
            Prediction.timestamp.desc()
        ).all()
    else:
        preds = Prediction.query.order_by(Prediction.timestamp.desc()).limit(50).all()
    return render_template('dashboard/history.html', predictions=preds)
