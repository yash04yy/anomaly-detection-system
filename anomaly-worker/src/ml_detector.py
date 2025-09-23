import numpy as np
from sklearn.ensemble import IsolationForest

class IsolationForestDetector:
    def __init__(self, batch_size=20, contamination=0.1):
        self.batch_size = batch_size
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.buffer = []

    def add_metric(self, value):
        self.buffer.append([value])  # sklearn expects 2D array
        if len(self.buffer) >= self.batch_size:
            return self._train_and_detect()
        return []

    def _train_and_detect(self):
        X = np.array(self.buffer)
        self.model.fit(X)
        preds = self.model.predict(X)  # 1 = normal, -1 = anomaly
        anomalies = [float(val[0]) for val, pred in zip(self.buffer, preds) if pred == -1]
        self.buffer.clear()
        return anomalies
