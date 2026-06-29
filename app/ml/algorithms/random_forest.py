import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


class RandomForestCropModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100, max_depth=None, random_state=42, n_jobs=-1
        )
        self.accuracy = None

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def evaluate(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)
        return {
            'accuracy': self.accuracy,
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'report': classification_report(y_test, y_pred, output_dict=True),
        }

    def predict(self, X):
        return self.model.predict(X)[0]

    def predict_proba(self, X):
        return self.model.predict_proba(X)[0]

    def get_feature_importance(self):
        return self.model.feature_importances_

    def save(self, path='models/random_forest_model.pkl'):
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def load(self, path='models/random_forest_model.pkl'):
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
