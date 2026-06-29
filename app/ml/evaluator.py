import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.preprocessing import label_binarize


class ModelEvaluator:
    FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

    @staticmethod
    def accuracy(y_true, y_pred):
        return accuracy_score(y_true, y_pred)

    @staticmethod
    def f1(y_true, y_pred, average='weighted'):
        return f1_score(y_true, y_pred, average=average)

    @staticmethod
    def confusion(y_true, y_pred):
        return confusion_matrix(y_true, y_pred).tolist()

    @staticmethod
    def classification(y_true, y_pred):
        return classification_report(y_true, y_pred, output_dict=True)

    @staticmethod
    def roc_auc_multiclass(y_true, y_proba, classes):
        try:
            y_bin = label_binarize(y_true, classes=range(len(classes)))
            return float(roc_auc_score(y_bin, y_proba, multi_class='ovr', average='weighted'))
        except ValueError:
            return None

    @staticmethod
    def feature_importance(model, feature_names=None):
        if not hasattr(model, 'feature_importances_'):
            return {}
        names = feature_names or ModelEvaluator.FEATURE_NAMES
        importances = model.feature_importances_
        return {names[i]: float(importances[i]) for i in range(len(names))}

    @staticmethod
    def summarize(model_wrapper, X_test, y_test, label_encoder=None):
        y_pred = model_wrapper.model.predict(X_test)
        result = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1_weighted': f1_score(y_test, y_pred, average='weighted'),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'report': classification_report(y_test, y_pred, output_dict=True),
        }
        if hasattr(model_wrapper, 'get_feature_importance'):
            fi = model_wrapper.get_feature_importance()
            result['feature_importance'] = {
                ModelEvaluator.FEATURE_NAMES[i]: float(fi[i]) for i in range(len(fi))
            }
        if hasattr(model_wrapper, 'predict_proba') and label_encoder is not None:
            try:
                proba = model_wrapper.model.predict_proba(X_test)
                result['roc_auc'] = ModelEvaluator.roc_auc_multiclass(
                    y_test, proba, label_encoder.classes_
                )
            except Exception:
                result['roc_auc'] = None
        return result
