# Core/fid.py - Phase 3: Decision Logic Upgrade

class FailureIntelligence:
    def __init__(self):
        # Thresholds for decision making
        self.TILT_THRESHOLD = 15.0  # Degrees
        self.CRITICAL_TILT = 45.0    # Degrees
        self.MAX_LATENCY = 0.12     # 120ms (slightly over our 10Hz target)

    def evaluate_system(self, telemetry, latency):
        """
        Analyzes synced data and returns a Control State.
        """
        pitch = abs(telemetry.get('pitch', 0))
        roll = abs(telemetry.get('roll', 0))
        
        # 1. Check for Critical Failures (The "Stop" Reflex)
        if telemetry.get('status') == "GHOST_DIVE" or pitch > self.CRITICAL_TILT:
            return "STOP"

        # 2. Check for Timing Issues (The "Safe Mode" Reflex)
        if latency > self.MAX_LATENCY:
            return "SAFE_MODE"

        # 3. Check for Physical Instability (The "Correction" Reflex)
        if pitch > self.TILT_THRESHOLD or roll > self.TILT_THRESHOLD:
            return "CORRECTIVE_ACTION"

        # 4. All systems clear
        return "NOMINAL"

    def get_state_description(self, state):
        descriptions = {
            "NOMINAL": "System healthy. Proceed with mission.",
            "SAFE_MODE": "Latency detected. Reducing gait speed.",
            "CORRECTIVE_ACTION": "Stability compromised. Engaging balance reflexes.",
            "STOP": "Critical failure. Immediate actuator shutdown."
        }
        return descriptions.get(state, "UNKNOWN")