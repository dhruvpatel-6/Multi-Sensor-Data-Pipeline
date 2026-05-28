import json
from datetime import datetime

class FaultPropagationEngine:
    def __init__(self):
        # Master propagation matrix definition mapping trigger to consequences
        self.matrix = {
            "ACTUATOR_BUS_TIMEOUT": {
                "severity": "DEGRADED",
                "telemetry_state": "DEGRADED",
                "control_state": "SAFE_FALLBACK",
                "gait_mode": "RECOVERY_PULSE",
                "actuator_action": "CURRENT_LIMITED",
                "replay_tag": "FAULT_BUS_TIMEOUT_DEGRADED_PERFORMANCE"
            },
            "GHOST_DIVE_FAULT": {
                "severity": "EMERGENCY_STOP",
                "telemetry_state": "INVALID_STRUCTURE",
                "control_state": "SAFE_FALLBACK",
                "gait_mode": "STAND",
                "actuator_action": "THERMAL_FAULT",
                "replay_tag": "CRITICAL_GHOST_DIVE_COMMAND_HALT"
            },
            "NOMINAL_CLEAR": {
                "severity": "NOMINAL",
                "telemetry_state": "VALIDATED",
                "control_state": "POSITION",
                "gait_mode": "TROTTING",
                "actuator_action": "OPERATIONAL",
                "replay_tag": "LIVE_STREAM"
            }
        }

    def propagate_fault(self, active_fault, base_telemetry_frame):
        """Mutates a unified telemetry frame based on active fault rules."""
        if active_fault not in self.matrix:
            return base_telemetry_frame

        rules = self.matrix[active_fault]
        mutated_frame = base_telemetry_frame.copy()

        # Update root state properties
        mutated_frame["health_status"] = rules["severity"]
        mutated_frame["failure_reason"] = active_fault
        mutated_frame["timestamp"] = datetime.utcnow().isoformat() + "Z"

        # Propagate to Rajaryan's Control Layer
        mutated_frame["control_state"] = base_telemetry_frame["control_state"].copy()
        mutated_frame["control_state"]["control_mode"] = rules["control_state"]
        mutated_frame["control_state"]["gait_mode"] = rules["gait_mode"]
        if rules["severity"] == "EMERGENCY_STOP":
            mutated_frame["control_state"]["recovery_state"] = "SELF_RIGHTING"
            mutated_frame["control_state"]["target_velocity"] = [0.0, 0.0, 0.0]

        # Propagate to Rugved's Actuator Hardware Layer
        mutated_frame["actuation_state"] = base_telemetry_frame["actuation_state"].copy()
        mutated_frame["actuation_state"]["driver_status"] = rules["actuator_action"]
        if active_fault == "ACTUATOR_BUS_TIMEOUT":
            mutated_frame["actuation_state"]["bus_health"] = "TIMEOUT_CRITICAL"

        # Propagate to Observability Layer & System Health
        mutated_frame["system_health"] = base_telemetry_frame["system_health"].copy()
        mutated_frame["system_health"]["schema_status"] = rules["telemetry_state"]
        mutated_frame["system_health"]["replay_status"] = "REPLAY_ACTIVE"
        
        # Inject Replay Annotation/Tag
        mutated_frame["meta"] = {
            "replay_status_annotation": rules["replay_tag"],
            "propagation_timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return mutated_frame

if __name__ == "__main__":
    propagator = FaultPropagationEngine()
    
    # Base nominal convergent frame layout from Phase 2
    sample_frame = {
        "timestamp": "2026-05-28T07:54:21.102941Z", "trace_id": "TRC-2026-DEMO94EC",
        "health_status": "NOMINAL", "failure_reason": "NONE", "loop_latency_ms": 4.12,
        "control_state": {"gait_mode": "TROTTING", "target_velocity": [1.2, 0.0, 0.1], "control_mode": "POSITION", "recovery_state": "INACTIVE"},
        "locomotion_state": {"hip_angles": [0.12, -0.11, 0.13, -0.12], "knee_angles": [0.65, 0.64, 0.66, 0.65], "foot_positions": [[0.18, 0.15, -0.31], [0.18, -0.15, -0.30], [-0.22, 0.15, -0.31], [-0.22, -0.15, -0.30]], "support_polygon_state": "DYNAMIC_TRI", "stability_margin": 84.5},
        "terrain_state": {"terrain_type": "CONCRETE_DRY", "slip_probability": 0.04, "traction_state": "OPTIMAL", "incline_estimate": 0.015},
        "actuation_state": {"joint_torque": [14.2, 12.8, 15.1, 13.9], "driver_status": "OPERATIONAL", "bus_health": "HEALTHY", "thermal_state": [42.5, 41.0, 43.8, 42.1]},
        "system_health": {"watchdog_status": "HEARTBEAT_OK", "timing_status": "DETERMINISTIC", "schema_status": "VALIDATED", "replay_status": "LIVE_STREAM"}
    }

    # Execute propagation sequence for timeout injection
    degraded_result = propagator.propagate_fault("ACTUATOR_BUS_TIMEOUT", sample_frame)
    print("=== PROPAGATION OUTPUT: ACTUATOR_BUS_TIMEOUT ===")
    print(json.dumps(degraded_result, indent=2))    