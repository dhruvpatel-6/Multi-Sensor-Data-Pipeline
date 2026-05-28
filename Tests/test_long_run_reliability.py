import json
import time
import random
import sys
from datetime import datetime
from metrics.observability_engine import ObservabilityEngine
from Core.fault_propagator import FaultPropagationEngine

def execute_sustained_reliability_run(target_frames=350):
    print("=====================================================================")
    print(f" LAUNCHING PHASE 6: SUSTAINED RELIABILITY STRESS TEST ({target_frames} FRAMES) ")
    print("=====================================================================\n")
    
    base_frame = {
        "trace_id": "TRC-2026-LONGEXP", "health_status": "NOMINAL", "failure_reason": "NONE",
        "control_state": {"gait_mode": "TROTTING", "target_velocity": [1.2, 0.0, 0.1], "control_mode": "POSITION", "recovery_state": "INACTIVE"},
        "locomotion_state": {"hip_angles": [0.12, -0.11, 0.13, -0.12], "knee_angles": [0.65, 0.64, 0.66, 0.65], "foot_positions": [[0.18, 0.15, -0.31], [0.18, -0.15, -0.30], [-0.22, 0.15, -0.31], [-0.22, -0.15, -0.30]], "support_polygon_state": "DYNAMIC_TRI", "stability_margin": 85.0},
        "terrain_state": {"terrain_type": "CONCRETE_DRY", "slip_probability": 0.02, "traction_state": "OPTIMAL", "incline_estimate": 0.01},
        "actuation_state": {"joint_torque": [12.0, 12.0, 12.0, 12.0], "driver_status": "OPERATIONAL", "bus_health": "HEALTHY", "thermal_state": [40.0, 40.0, 40.0, 40.0]},
        "system_health": {"watchdog_status": "HEARTBEAT_OK", "timing_status": "DETERMINISTIC", "schema_status": "VALIDATED", "replay_status": "LIVE_STREAM"}
    }

    simulated_log_path = "logs/long_run_reliability_source.json"
    propagator = FaultPropagationEngine()
    
    # Generate continuous timeline entries with artificial real-world variations
    with open(simulated_log_path, "w") as f:
        virtual_seq = 1
        base_temp = 40.0
        
        for frame_idx in range(1, target_frames + 1):
            current_frame = base_frame.copy()
            current_frame["timestamp"] = datetime.utcnow().isoformat() + "Z"
            
            # Simulate artificial CPU execution latency jitter (Target baseline = 4.0ms)
            # Introduce a systematic timing drift drift over time
            if frame_idx < 100:
                current_frame["loop_latency_ms"] = round(4.0 + random.uniform(-0.1, 0.1), 3)
            elif frame_idx < 250:
                current_frame["loop_latency_ms"] = round(4.2 + random.uniform(-0.1, 0.3), 3) # Mild scheduling jitter
            else:
                current_frame["loop_latency_ms"] = round(4.5 + random.uniform(0.1, 1.2), 3)  # Gradual accumulation overhead
            
            # Simulate gradual motor thermal accumulation across extended operation
            base_temp += random.uniform(-0.02, 0.08)
            current_frame["actuation_state"]["thermal_state"] = [round(base_temp + random.uniform(-0.5, 0.5), 1) for _ in range(4)]
            
            # Inject explicit behavioral anomalies at fixed intervals to verify replay integrity
            if frame_idx == 120:
                # Dropped Frame Check: Intentionally skip a sequence number
                virtual_seq += 1 
            elif frame_idx == 220:
                # Fault Propagation Check: Inject temporary bus failure state
                current_frame = propagator.propagate_fault("ACTUATOR_BUS_TIMEOUT", current_frame)
            elif frame_idx == 310:
                # Anomaly Trigger: Simulate terrain slip condition
                current_frame["terrain_state"]["slip_probability"] = 0.72
                current_frame["terrain_state"]["traction_state"] = "SLIPPING"
            
            # Inject tracking metadata
            if "meta" not in current_frame:
                current_frame["meta"] = {}
            current_frame["meta"]["sequence_number"] = virtual_seq
            
            f.write(json.dumps(current_frame) + "\n")
            virtual_seq += 1

    # Execute metrics processing engine over the sustained file footprint
    obs_engine = ObservabilityEngine()
    obs_engine.process_session_telemetry(simulated_log_path)
    dashboard_results = obs_engine.generate_dashboard_json()
    
    print("\n=====================================================================")
    print(" SUSTAINED RELIABILITY TEST COMPLETED SUCCESSFULLY                   ")
    print("=====================================================================")
    print(json.dumps(dashboard_results, indent=2))
    
    # Save formal output verification results
    with open("Docs/long_run_reliability_results.json", "w") as out:
        json.dump(dashboard_results, out, indent=2)

if __name__ == "__main__":
    execute_sustained_reliability_run(target_frames=350)





# execute with 
#$env:PYTHONPATH="."
#.\.venv\Scripts\python.exe Tests/test_long_run_reliability.py