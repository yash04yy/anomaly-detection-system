from collections import deque
import statistics

class MovingAverageDetector:
    def __init__(self, window_size=5, threshold=20):
        self.window_size = window_size
        self.threshold = threshold
        self.window = deque(maxlen=window_size)

    def detect(self, value):
        self.window.append(value)
        if len(self.window) < self.window_size:
            return False
        avg = statistics.mean(self.window)
        if abs(value - avg) > self.threshold:
            return True
        return False
