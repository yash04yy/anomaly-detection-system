import os
import json
import numpy as np
from sklearn.ensemble import IsolationForest
from .persistence import save_anomaly

class IsolationForestDetector:
    def __init__(
        self,
        batch_size=None,
        contamination=None,
        metric_name="metric",
        smoothing_alpha=None,
        min_anomaly_consec=None
    ):
        self.batch_size = int(batch_size or os.getenv("IF_BATCH_SIZE", 20))
        self.contamination = float(contamination or os.getenv("IF_CONTAMINATION", 0.1))
        self.alpha = float(smoothing_alpha or os.getenv("IF_SMOOTHING_ALPHA", 0.25))
        self.min_anomaly_consec = int(min_anomaly_consec or os.getenv("IF_MIN_ANOMALY_CONSEC", 3))
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
        self.buffer = []
        self.metric_name = metric_name
        self.smoothed_prev = None
        self.score_history = []
        self.std_history = []
        self.anomaly_streak = 0

    def add_metric(self, value):
        if self.smoothed_prev is None:
            smoothed_value = value
        else:
            smoothed_value = self.alpha * value + (1 - self.alpha) * self.smoothed_prev
        self.smoothed_prev = smoothed_value

        self.buffer.append([smoothed_value])
        if len(self.buffer) >= self.batch_size:
            return self._train_and_detect()
        return []

    def _train_and_detect(self):
        X = np.array(self.buffer)
        self.model.fit(X)
        preds = self.model.predict(X)
        scores = self.model.decision_function(X)

        anomalies = []
        self.score_history.extend(scores.tolist())
        std_win = 20
        if len(self.score_history) >= std_win:
            recent = self.score_history[-std_win:]
            std = np.std(recent)
            self.std_history.append(std)
        if self.std_history:
            dynamic_threshold = np.mean(self.std_history) * 2.5
        else:
            dynamic_threshold = 3.0
        for i, (val, pred, score) in enumerate(zip(self.buffer, preds, scores)):
            v = float(val[0])
            is_anomaly = pred == -1
            zscore = abs((score - np.mean(scores)) / (np.std(scores) + 1e-8))

            if zscore > dynamic_threshold:
                self.anomaly_streak += 1
            else:
                self.anomaly_streak = 0

            if is_anomaly and self.anomaly_streak >= self.min_anomaly_consec:
                context = {
                    "buffer": [float(x[0]) for x in self.buffer],
                    "value": float(v),
                    "score": float(score),
                    "z_score": float(zscore),
                    "dynamic_threshold": float(dynamic_threshold),
                    "smoothing_alpha": float(self.alpha),
                    "streak": int(self.anomaly_streak)
                }
                config = {
                    "batch_size": int(self.batch_size),
                    "contamination": float(self.contamination),
                    "smoothing_alpha": float(self.alpha),
                    "dynamic_threshold": float(dynamic_threshold),
                    "min_consecutive": int(self.min_anomaly_consec)
                }
                anomalies.append(v)
                save_anomaly(
                    metric_name=self.metric_name,
                    value=float(v),
                    threshold=float(dynamic_threshold),
                    status="anomaly",
                    detection_method="IsolationForest",
                    anomaly_score=float(score),
                    context=json.dumps(context),
                    config=json.dumps(config)
                )

        self.buffer.clear()
        return anomalies
