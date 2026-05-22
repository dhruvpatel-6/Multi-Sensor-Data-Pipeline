# Core/fid.py
# Phase 5: Hardened Failure Intelligence Layer

class FailureIntelligence:
    def __init__(self):
        pass

    def evaluate_system(self, json_contract_data):
        """
        Audits the incoming canonical contract for multi-boundary anomalies.
        Returns: (health_status, failure_reason)
        """
        # Safely extract values directly from the contract dictionary
        health = json_contract_data.get("health_status", "NOMINAL")
        reason = json_contract_data.get("failure_reason", "NONE")
        imu = json_contract_data.get("imu_data", {})
        joints = json_contract_data.get("joint_states", {})
        latency = json_contract_data.get("latency_ms", 0.0)

        # Failure Mode 1: Missing Actuator Data Boundary (Rugved Bus Timeout)
        if (joints.get("hip") == 0.0 and joints.get("knee") == 0.0 and health == "DEGRADED") or reason == "ACTUATOR_BUS_TIMEOUT":
            return "DEGRADED", "ACTUATOR_BUS_TIMEOUT"

        # Failure Mode 2: Corrupt Sensor Packet (Ghost Dive Anomaly)
        if imu.get("pitch") == -99.0 or health == "CRITICAL" or reason == "GHOST_DIVE_FAULT":
            return "CRITICAL", "GHOST_DIVE_FAULT"

        # Failure Mode 3: Latency Spike Overflow (>15ms budget)
        if latency > 15.0:
            return "DEGRADED", "LATENCY_SPIKE_DETECTED"

        return "NOMINAL", "NONE"