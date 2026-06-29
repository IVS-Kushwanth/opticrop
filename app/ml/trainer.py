import os

from sklearn.model_selection import cross_val_score

from app.ml.algorithms.decision_tree import DecisionTreeCropModel
from app.ml.algorithms.kmeans import KMeansCropModel
from app.ml.algorithms.knn import KNNCropModel
from app.ml.algorithms.logistic import LogisticCropModel
from app.ml.algorithms.random_forest import RandomForestCropModel
from app.ml.evaluator import ModelEvaluator
from app.ml.preprocessor import CropPreprocessor


class ModelTrainer:
    def __init__(self, data_path='data/Crop_recommendation.csv', models_dir='models'):
        self.data_path = data_path
        self.models_dir = models_dir
        self.preprocessor = CropPreprocessor()
        self.results = {}

    def load_and_prepare(self):
        df = self.preprocessor.load_data(self.data_path)
        X, y = self.preprocessor.prepare_features(df, fit=True)
        return self.preprocessor.split_data(X, y)

    def train_all(self):
        os.makedirs(self.models_dir, exist_ok=True)
        X_train, X_test, y_train, y_test = self.load_and_prepare()
        self.preprocessor.save(os.path.join(self.models_dir, 'scaler.pkl'))

        trainers = [
            ('knn', KNNCropModel(n_neighbors=5), 'knn_model.pkl'),
            ('logistic', LogisticCropModel(), 'logistic_model.pkl'),
            ('decision_tree', DecisionTreeCropModel(), 'decision_tree_model.pkl'),
            ('random_forest', RandomForestCropModel(), 'random_forest_model.pkl'),
        ]

        for name, model, filename in trainers:
            model.train(X_train, y_train)
            eval_result = model.evaluate(X_test, y_test)
            cv_scores = cross_val_score(model.model, X_train, y_train, cv=5)
            eval_result['cv_mean'] = float(cv_scores.mean())
            eval_result['cv_std'] = float(cv_scores.std())
            self.results[name] = eval_result
            model.save(os.path.join(self.models_dir, filename))

        km = KMeansCropModel(n_clusters=22)
        km.train(X_train, y_train, self.preprocessor.label_encoder)
        km.save(os.path.join(self.models_dir, 'kmeans_model.pkl'))
        self.results['kmeans'] = {'note': 'unsupervised clustering model'}

        return self.results

    def get_evaluation_summary(self):
        return ModelEvaluator.summarize
