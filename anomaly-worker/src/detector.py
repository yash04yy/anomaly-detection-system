import os
import json
from collections import deque
import statistics
from .persistence import save_anomaly

class MovingAverageDetector:
    def __init__(self, window_size=None, threshold=None, metric_name="metric"):
        self.window_size = int(window_size or os.getenv("MA_WINDOW_SIZE", 5))
        self.threshold = float(threshold or os.getenv("MA_THRESHOLD", 20))
        self.window = deque(maxlen=self.window_size)
        self.metric_name = metric_name

    def detect(self, value):
        self.window.append(value)
        if len(self.window) < self.window_size:
            return False
        avg = statistics.mean(self.window)
        deviation = abs(value - avg)
        is_anomaly = deviation > self.threshold

        if is_anomaly:
            context = {
                "value": value,
                "window": list(self.window),
                "mean": avg,
                "deviation": deviation,
                "threshold": self.threshold
            }
            config = {
                "window_size": self.window_size,
                "threshold": self.threshold
            }
            save_anomaly(
                metric_name=self.metric_name,
                value=value,
                threshold=self.threshold,
                status="anomaly",
                detection_method="MovingAverage",
                anomaly_score=deviation,
                context=json.dumps(context),
                config=json.dumps(config)
            )
            return True
        return False
