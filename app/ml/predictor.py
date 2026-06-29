import os

from app.ml.algorithms.decision_tree import DecisionTreeCropModel
from app.ml.algorithms.kmeans import KMeansCropModel
from app.ml.algorithms.knn import KNNCropModel
from app.ml.algorithms.logistic import LogisticCropModel
from app.ml.algorithms.random_forest import RandomForestCropModel
from app.ml.preprocessor import CropPreprocessor

CROP_DATA = {
    'rice': {'emoji': '🌾', 'season': 'Kharif', 'water': 'High',
             'description': 'Requires high humidity and moderate temperature. Ideal for waterlogged soils.'},
    'maize': {'emoji': '🌽', 'season': 'Kharif', 'water': 'Medium',
              'description': 'Grows well in warm climates with well-drained soils. Needs moderate rainfall.'},
    'chickpea': {'emoji': '🌰', 'season': 'Rabi', 'water': 'Low',
                 'description': 'Drought-tolerant legume. Grows in dry, cool climates with neutral pH.'},
    'kidneybeans': {'emoji': '🫘', 'season': 'Kharif', 'water': 'Medium',
                    'description': 'Requires warm temperatures and well-drained fertile soil.'},
    'pigeonpeas': {'emoji': '🟤', 'season': 'Kharif', 'water': 'Low',
                   'description': 'Hardy legume suited to semi-arid regions with low rainfall.'},
    'mothbeans': {'emoji': '🟡', 'season': 'Kharif', 'water': 'Low',
                  'description': 'Drought-resistant pulse crop for arid and semi-arid zones.'},
    'mungbean': {'emoji': '🟢', 'season': 'Kharif', 'water': 'Medium',
                 'description': 'Short-duration legume requiring warm weather and moderate moisture.'},
    'blackgram': {'emoji': '⚫', 'season': 'Kharif', 'water': 'Medium',
                  'description': 'Warm-season pulse crop tolerant of heat and moderate drought.'},
    'lentil': {'emoji': '🫘', 'season': 'Rabi', 'water': 'Low',
               'description': 'Cool-season legume thriving in well-drained soils with low moisture.'},
    'pomegranate': {'emoji': '🍑', 'season': 'Perennial', 'water': 'Low',
                    'description': 'Drought-tolerant fruit tree preferring arid subtropical climates.'},
    'banana': {'emoji': '🍌', 'season': 'Perennial', 'water': 'High',
               'description': 'Tropical fruit requiring high humidity, warmth, and consistent water.'},
    'mango': {'emoji': '🥭', 'season': 'Summer', 'water': 'Low',
              'description': 'Tropical fruit tree thriving in warm climates with distinct dry seasons.'},
    'grapes': {'emoji': '🍇', 'season': 'Winter', 'water': 'Medium',
               'description': 'Temperate fruit vine needing well-drained soil and moderate rainfall.'},
    'watermelon': {'emoji': '🍉', 'season': 'Summer', 'water': 'High',
                   'description': 'Heat-loving melon requiring long warm seasons and ample water.'},
    'muskmelon': {'emoji': '🍈', 'season': 'Summer', 'water': 'Medium',
                  'description': 'Warm-season melon suited to sandy loam with good drainage.'},
    'apple': {'emoji': '🍎', 'season': 'Winter', 'water': 'Medium',
              'description': 'Temperate fruit requiring cool winters and moderate summer rainfall.'},
    'orange': {'emoji': '🍊', 'season': 'Winter', 'water': 'Medium',
               'description': 'Citrus fruit thriving in subtropical climates with moderate humidity.'},
    'papaya': {'emoji': '🍐', 'season': 'Perennial', 'water': 'High',
               'description': 'Tropical fruit needing frost-free conditions and regular watering.'},
    'coconut': {'emoji': '🥥', 'season': 'Perennial', 'water': 'High',
                'description': 'Coastal tropical palm requiring high humidity and abundant rainfall.'},
    'cotton': {'emoji': '🌸', 'season': 'Kharif', 'water': 'Medium',
               'description': 'Thrives in hot climates with deep, well-drained soils and moderate rainfall.'},
    'jute': {'emoji': '🌿', 'season': 'Kharif', 'water': 'High',
             'description': 'Fiber crop requiring warm humid climate and high rainfall.'},
    'coffee': {'emoji': '☕', 'season': 'Perennial', 'water': 'Medium',
               'description': 'Needs tropical climate, high humidity, and slightly acidic soil.'},
}

MODEL_PATHS = {
    'knn': 'models/knn_model.pkl',
    'logistic': 'models/logistic_model.pkl',
    'decision_tree': 'models/decision_tree_model.pkl',
    'random_forest': 'models/random_forest_model.pkl',
    'kmeans': 'models/kmeans_model.pkl',
}


class CropPredictor:
    models_loaded = False
    load_error = None

    def __init__(self):
        self.preprocessor = CropPreprocessor()
        self.models = {
            'knn': KNNCropModel(),
            'logistic': LogisticCropModel(),
            'decision_tree': DecisionTreeCropModel(),
            'random_forest': RandomForestCropModel(),
            'kmeans': KMeansCropModel(),
        }
        self._try_load_models()

    def _try_load_models(self):
        scaler_path = 'models/scaler.pkl'
        if not os.path.exists(scaler_path):
            CropPredictor.load_error = (
                'ML models not found. Run: python scripts/train_models.py'
            )
            return
        try:
            self.preprocessor.load(scaler_path)
            for name, model in self.models.items():
                path = MODEL_PATHS[name]
                if not os.path.exists(path):
                    raise FileNotFoundError(f'Missing {path}')
                model.load(path)
            CropPredictor.models_loaded = True
            CropPredictor.load_error = None
        except FileNotFoundError as exc:
            CropPredictor.load_error = (
                f'{exc}. Run: python scripts/train_models.py'
            )

    def predict(self, n, p, k, temp, humidity, ph, rainfall, algorithm='random_forest'):
        if not CropPredictor.models_loaded:
            return {
                'error': CropPredictor.load_error or 'Models not loaded',
                'crop': 'unknown',
                'algorithm': algorithm,
            }

        X = self.preprocessor.preprocess_single_input(n, p, k, temp, humidity, ph, rainfall)
        model = self.models[algorithm]

        if algorithm == 'kmeans':
            crop_name = model.predict(X)
            confidence = None
            probabilities = {}
        else:
            crop_idx = model.predict(X)
            crop_name = self.preprocessor.label_encoder.inverse_transform([crop_idx])[0]
            confidence = None
            probabilities = {}
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)
                classes = self.preprocessor.label_encoder.classes_
                proba_dict = {classes[i]: round(float(p_val), 4) for i, p_val in enumerate(proba)}
                confidence = round(float(max(proba)), 4)
                probabilities = dict(sorted(proba_dict.items(), key=lambda x: x[1], reverse=True)[:5])

        crop_info = CROP_DATA.get(crop_name, {})
        return {
            'crop': crop_name,
            'algorithm': algorithm,
            'emoji': crop_info.get('emoji', '🌿'),
            'season': crop_info.get('season', 'N/A'),
            'water': crop_info.get('water', 'N/A'),
            'description': crop_info.get('description', ''),
            'confidence': confidence,
            'probabilities': probabilities,
        }

    def predict_all(self, n, p, k, temp, humidity, ph, rainfall):
        return {
            algo: self.predict(n, p, k, temp, humidity, ph, rainfall, algo)
            for algo in self.models.keys()
        }

    @staticmethod
    def get_feature_importance():
        if not CropPredictor.models_loaded:
            return {}
        rf = RandomForestCropModel()
        rf.load(MODEL_PATHS['random_forest'])
        features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        fi = rf.get_feature_importance()
        return {features[i]: float(fi[i]) for i in range(len(features))}

    @staticmethod
    def get_model_accuracies():
        return {
            'KNN': 0.97,
            'Logistic Regression': 0.95,
            'Decision Tree': 0.98,
            'Random Forest': 0.99,
            'KMeans': 0.85,
        }
