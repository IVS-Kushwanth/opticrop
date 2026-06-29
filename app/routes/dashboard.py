from collections import Counter
from datetime import datetime, timedelta

from flask import Blueprint, render_template, session
from sqlalchemy import func

from app.extensions import db
from app.ml.predictor import CropPredictor
from app.models.prediction import Prediction
from app.models.user import User

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def index():
    total_predictions = Prediction.query.count()
    total_users = User.query.count()
    recent = Prediction.query.order_by(Prediction.timestamp.desc()).limit(5).all()
    user_predictions = 0
    if session.get('user_id'):
        user_predictions = Prediction.query.filter_by(user_id=session['user_id']).count()

    return render_template(
        'dashboard/index.html',
        total_predictions=total_predictions,
        total_users=total_users,
        user_predictions=user_predictions,
        recent_predictions=recent,
    )


@dashboard_bp.route('/analytics')
def analytics():
    return render_template(
        'dashboard/analytics.html',
        model_error=CropPredictor.load_error,
    )


@dashboard_bp.route('/compare')
def compare_page():
    return render_template('predict/compare.html')
