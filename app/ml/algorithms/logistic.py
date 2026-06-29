import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


class LogisticCropModel:
    def __init__(self):
        self.model = LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs')
        self.accuracy = None

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def evaluate(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)
        return {'accuracy': self.accuracy, 'report': classification_report(y_test, y_pred, output_dict=True)}

    def predict(self, X):
        return self.model.predict(X)[0]

    def predict_proba(self, X):
        return self.model.predict_proba(X)[0]

    def save(self, path='models/logistic_model.pkl'):
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def load(self, path='models/logistic_model.pkl'):
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
