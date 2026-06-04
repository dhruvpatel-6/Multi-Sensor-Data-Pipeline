import json
from Core.fault_propagator import AdvancedFaultPropagator
# Sample baseline frame matching target specifications
sample_base = {
    "timestamp": "2026-06-03T12:00:00.000Z", 
    "trace_id": "TRC-2026-DEMO1234", 
    "health_status": "NOMINAL", 
    "loop_latency_ms": 4.0,
    "control_state": {"gait_mode": "TROTTING", "target_velocity": [1.0, 0.0, 0.0], "control_mode": "POSITION", "recovery_state": "INACTIVE"},
    "locomotion_state": {"hip_angles": [0.0, 0.0, 0.0, 0.0], "knee_angles": [0.5, 0.5, 0.5, 0.5], "foot_positions": [[0,0,0],[0,0,0],[0,0,0],[0,0,0]], "support_polygon_state": "STABLE_QUAD", "stability_margin": 100.0},
    "terrain_state": {"terrain_type": "CONCRETE_DRY", "slip_probability": 0.0, "traction_state": "OPTIMAL", "incline_estimate": 0.0},
    "actuation_state": {"joint_torque": [10.0, 10.0, 10.0, 10.0], "driver_status": "OPERATIONAL", "bus_health": "HEALTHY", "thermal_state": [40.0, 40.0, 40.0, 40.0]},
    "system_health": {"watchdog_status": "HEARTBEAT_OK", "timing_status": "DETERMINISTIC", "schema_status": "VALIDATED", "replay_status": "LIVE_STREAM"}
}

propagator = AdvancedFaultPropagator()

print("[+] Injecting THERMAL_ESCALATION Fault Into Advanced Core Pipeline...")
propagator.inject_fault("THERMAL_ESCALATION")
mutated_frame = propagator.process_frame(sample_base)

print(f"[-] Mutated System Health Status State: {mutated_frame['health_status']}")
print(f"[-] Mutated System Thermal Vector Readings: {mutated_frame['actuation_state']['thermal_state']}")
print(f"[-] Mutated Driver Operational Profile Tag: {mutated_frame['actuation_state']['driver_status']}")