import time

class FailureIntelligence:
    def __init__(self):
        # Phase 3 & 4 Variables
        self.imu_history = []
        self.max_history = 10
        self.last_update_time = time.time()
        self.TIMEOUT_THRESHOLD = 0.5  # 500ms limit for "Stale Data"

    def analyze_intelligence(self, imu_z, dist, contact):
        """
        PHASE 4: Handles Missing Data, Delays, and Spikes.
        """
        current_time = time.time()

        # --- ROBUSTNESS CHECK 1: Delayed Packets / Stale Data ---
        time_delta = current_time - self.last_update_time
        if time_delta > self.TIMEOUT_THRESHOLD:
            # Detects if the simulator has stopped or lagged
            self.last_update_time = current_time # Reset to prevent loop
            return "CRITICAL", "STALE_DATA_TIMEOUT", 0.0
        
        self.last_update_time = current_time

        # --- ROBUSTNESS CHECK 2: Missing Data Guard ---
        if imu_z is None or dist is None:
            return "DEGRADED", "MISSING_SENSOR_DATA", 0.0

        # --- ROBUSTNESS CHECK 3: Sensor Spike Detection (NEW) ---
        # Detects the 99.9m spike injected in main_telemetry.py
        if dist > 10.0:
            return "CRITICAL", "SENSOR_SPIKE_DETECTED", 0.0

        # --- Phase 3 Logic: Trend Analysis ---
        self.imu_history.append(imu_z)
        if len(self.imu_history) > self.max_history:
            self.imu_history.pop(0)

        # Calculate Stability (Variance)
        imu_variance = round(max(self.imu_history) - min(self.imu_history), 4)
        is_imu_stable = imu_variance < 0.1

        # --- Multi-Sensor Validation: Conflict Detection ---
        # Example: Robot thinks it's in the air but distance is very low
        if is_imu_stable and dist < 0.5 and contact == "IN_AIR":
            return "DEGRADED", "SENSOR_CONFLICT", imu_variance

        # If all checks pass
        return "HEALTHY", "NOMINAL", imu_variance