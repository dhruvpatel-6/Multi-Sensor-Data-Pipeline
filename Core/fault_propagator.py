import json
import random
from datetime import datetime

class AdvancedFaultPropagator:
    def __init__(self):
        self.active_faults = {}

    def inject_fault(self, fault_type):
        """Registers an active fault signature into the execution loop."""
        self.active_faults[fault_type] = datetime.utcnow().isoformat() + "Z"

    def clear_fault(self, fault_type):
        if fault_type in self.active_faults:
            del self.active_faults[fault_type]

    def process_frame(self, base_frame):
        """Applies active fault modifications directly to the telemetry data frame."""
        mutated_frame = json.loads(json.dumps(base_frame))
        
        for fault in self.active_faults.keys():
            if fault == "SENSOR_CORRUPTION":
                mutated_frame["locomotion_state"]["hip_angles"] = [999.9, -999.9, 0.0, 0.0]
                mutated_frame["system_health"]["schema_status"] = "MISMATCH_WARNING"
                
            elif fault == "IMU_DRIFT":
                mutated_frame["terrain_state"]["incline_estimate"] += 0.85  # Accumulated drift error
                mutated_frame["system_health"]["timing_status"] = "JITTER_WARNING"
                
            elif fault == "PACKET_LOSS":
                mutated_frame["system_health"]["watchdog_status"] = "MISSING_NODE"
                mutated_frame["health_status"] = "DEGRADED"
                
            elif fault == "BUS_TIMEOUT":
                mutated_frame["actuation_state"]["bus_health"] = "TIMEOUT_CRITICAL"
                mutated_frame["control_state"]["control_mode"] = "SAFE_FALLBACK"
                
            elif fault == "STALE_DATA":
                mutated_frame["timestamp"] = "2026-01-01T00:00:00.000000Z"  # Frozen clock artifact
                mutated_frame["system_health"]["timing_status"] = "DEADLINE_BREACH"
                
            elif fault == "ACTUATOR_SATURATION":
                mutated_frame["actuation_state"]["joint_torque"] = [45.0, 45.0, 45.0, 45.0]  # Max ceiling
                mutated_frame["actuation_state"]["driver_status"] = "CURRENT_LIMITED"
                
            elif fault == "THERMAL_ESCALATION":
                mutated_frame["actuation_state"]["thermal_state"] = [95.5, 96.2, 94.8, 95.1]
                mutated_frame["actuation_state"]["driver_status"] = "THERMAL_FAULT"
                mutated_frame["health_status"] = "EMERGENCY_STOP"
                
            elif fault == "LIMB_DEGRADATION":
                mutated_frame["locomotion_state"]["support_polygon_state"] = "UNSTABLE_DIAG"
                mutated_frame["control_state"]["gait_mode"] = "RECOVERY_PULSE"
                
            elif fault == "CONTACT_SENSOR_FAULTS":
                mutated_frame["locomotion_state"]["stability_margin"] = 0.0
                mutated_frame["health_status"] = "UNSTABLE"
                
            elif fault == "TIMING_JITTER":
                mutated_frame["loop_latency_ms"] = 18.75
                mutated_frame["system_health"]["timing_status"] = "JITTER_WARNING"
                
            elif fault == "CLOCK_SKEW":
                mutated_frame["trace_id"] = "TRC-9999-SKEWED_CLOCK"
                mutated_frame["system_health"]["timing_status"] = "DEADLINE_BREACH"
                
            elif fault == "TERRAIN_MISCLASSIFICATION":
                mutated_frame["terrain_state"]["terrain_type"] = "FLOWERBED_NOMINAL"
                mutated_frame["terrain_state"]["slip_probability"] = 0.95  # Severe logical mismatch
                
            elif fault == "SCHEMA_CORRUPTION":
                mutated_frame.pop("system_health")  # Destructive mutation breaking schema structure
                
            elif fault == "REPLAY_CORRUPTION":
                mutated_frame["system_health"]["replay_status"] = "INTEGRITY_COMPROMISED"
                mutated_frame["health_status"] = "DEGRADED"
                
            elif fault == "CONTROL_INSTABILITY":
                mutated_frame["control_state"]["recovery_state"] = "ACTIVE_BALANCING"
                mutated_frame["health_status"] = "UNSTABLE"
                
        return mutated_frame