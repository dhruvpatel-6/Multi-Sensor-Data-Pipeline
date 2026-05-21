class FailureIntelligence:
    def __init__(self):
        self.TILT_LIMIT = 45.0
        self.LOOP_MAX_ALLOWED_MS = 120.0  # Max non-negotiable timing threshold

    def evaluate_system(self, telemetry_packet, process_latency_ms):
        """
        Processes the strict Phase 1 canonical contract payload.
        Ensures clear fault classification without ever allowing a thread crash.
        """
        hardware_status = telemetry_packet.get("health_status", "NOMINAL")
        imu = telemetry_packet.get("imu_data", {})
        pitch = abs(imu.get("pitch", 0.0))
        
        # 1. Test Condition 2: Corrupt Sensor Packet / Physical Extreme Tipping Check
        if hardware_status == "CRITICAL" or pitch > self.TILT_LIMIT:
            return "STOP", "CRITICAL_SENSOR_CORRUPTION"

        # 2. Test Condition 1: Missing Actuator Data Check
        if hardware_status == "DEGRADED" or hardware_status == "MISSING_DATA":
            return "STOP", "MISSING_ACTUATOR_DATA"

        # 3. Test Condition 3: Real-Time Timing Delay Overrun Check
        if process_latency_ms > self.LOOP_MAX_ALLOWED_MS:
            return "DEGRADED", "LOOP_CLOCK_OVERRUN"

        return "NOMINAL", "NONE"