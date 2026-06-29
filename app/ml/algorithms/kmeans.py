import pickle

import numpy as np
from sklearn.cluster import KMeans


class KMeansCropModel:
    """KMeans clusters environmental conditions into 22 groups."""

    def __init__(self, n_clusters=22):
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.cluster_to_crop_map = {}

    def train(self, X_train, y_train, label_encoder):
        self.model.fit(X_train)
        cluster_labels = self.model.labels_
        for cluster_id in range(self.model.n_clusters):
            mask = cluster_labels == cluster_id
            if mask.sum() > 0:
                cluster_crops = y_train[mask]
                most_common = np.bincount(cluster_crops).argmax()
                self.cluster_to_crop_map[cluster_id] = label_encoder.classes_[most_common]

    def predict(self, X):
        cluster = self.model.predict(X)[0]
        return self.cluster_to_crop_map.get(cluster, 'unknown')

    def get_cluster_distances(self, X):
        return self.model.transform(X)[0]

    def save(self, path='models/kmeans_model.pkl'):
        with open(path, 'wb') as f:
            pickle.dump({'model': self.model, 'map': self.cluster_to_crop_map}, f)

    def load(self, path='models/kmeans_model.pkl'):
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.cluster_to_crop_map = data['map']
