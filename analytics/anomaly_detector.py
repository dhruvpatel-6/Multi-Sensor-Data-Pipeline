import numpy as np

class PredictiveAnomalyDetector:
    def __init__(self, window_size=30, z_threshold=2.5):
        self.z_threshold = z_threshold
        self.window_size = window_size
        self.latency_history = []

    def observe_and_predict(self, current_latency):
        self.latency_history.append(current_latency)
        
        if len(self.latency_history) > self.window_size:
            self.latency_history.pop(0)
            
        if len(self.latency_history) < 10:
            return False, 0.0
            
        mean_baseline = np.mean(self.latency_history[:-1])
        std_baseline = np.std(self.latency_history[:-1])
        
        if std_baseline == 0:
            std_baseline = 0.001
            
        z_score = abs(current_latency - mean_baseline) / std_baseline
        is_anomaly = z_score > self.z_threshold
        
        return bool(is_anomaly), float(round(z_score, 2))