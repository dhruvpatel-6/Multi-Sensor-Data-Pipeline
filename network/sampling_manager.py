import time

class TailBasedSamplingManager:
    def __init__(self, low_freq_hz=10, high_freq_hz=250):
        self.low_interval = 1.0 / low_freq_hz
        self.high_interval = 1.0 / high_freq_hz
        self.last_transmission_time = 0.0

    def evaluate_transmission_window(self, telemetry_frame):
        """
        Determines if the frame should be transmitted based on system urgency state.
        Returns (True/False, selected_mode_string)
        """
        current_time = time.time()
        
        # Extract operational states honestly from your canonical layout
        health = telemetry_frame.get("health_status", "NOMINAL")
        timing = telemetry_frame.get("system_health", {}).get("timing_status", "DETERMINISTIC")
        
        # Rule Engine: Trigger High-Fidelity stream if any anomaly layer is compromised
        is_anomaly = (health not in ["NOMINAL"]) or (timing != "DETERMINISTIC")
        
        required_interval = self.high_interval if is_anomaly else self.low_interval
        
        if (current_time - self.last_transmission_time) >= required_interval:
            self.last_transmission_time = current_time
            return True, "HIGH_FIDELITY_BURST" if is_anomaly else "LOW_POWER_HEARTBEAT"
            
        return False, "THROTTLED"