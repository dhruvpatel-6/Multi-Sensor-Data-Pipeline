# Tests/test_pipeline_continuity.py
import sys
import os
import time
import uuid
import random

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from Telemetry.telemetry_orchestrator import QuadrupedTelemetryOrchestrator

def run_live_dashboard_simulation(total_cycles=5):
    orchestrator = QuadrupedTelemetryOrchestrator()
    
    try:
        for tick in range(1, total_cycles + 1):
            unique_trace_id = f"TRC-2026-DEMO{uuid.uuid4().hex[:4].upper()}"
            
            # TRIGGER FAILURE CASCADE ON TICK 4 (Terrain -> Telemetry -> Instability -> Shutdown)
            if tick >= 4:
                locomotion_payload = {"gait_phase": "BOUNDING_FLIGHT", "terrain_type": "SLIPPERY_ICE"}
                stability_payload = {"com_position": [0.084, -0.091, 0.241], "tilt_state": {"pitch_rad": 0.65, "roll_rad": -0.48}, "stability_score": 35.5}
                mechanical_payload = {
                    "actuator_load": {"FL": 16.33, "FR": 16.33, "RL": 16.33, "RR": 16.33},
                    "structural_stress_zones": ["FRONT_LEFT_HIP_MOUNT"],
                    "torque_requirements": {"FL": {"knee": 85.4}}
                }
                thermal_payload = {"motor_saturation": {"FL": {"knee": 0.92}}}
            else:
                # Normal operational parameters
                locomotion_payload = {"gait_phase": "TROTTING", "terrain_type": "FLOWERBED_NOMINAL"}
                stability_payload = {"com_position": [0.001, 0.002, 0.295], "tilt_state": {"pitch_rad": 0.02, "roll_rad": 0.01}, "stability_score": 95.2}
                mechanical_payload = {
                    "actuator_load": {"FL": 16.33, "FR": 16.33, "RL": 16.33, "RR": 16.33},
                   "structural_stress_zones": ["NONE"],
                    "torque_requirements": {"FL": {"knee": 18.1}}
                }
                thermal_payload = {"motor_saturation": {"FL": {"knee": 0.21}}}

            orchestrator.execute_integration_cycle(
                locomotion_data=locomotion_payload,
                mechanical_data=mechanical_payload,
                stability_data=stability_payload,
                thermal_data=thermal_payload,
                upstream_trace_id=unique_trace_id
            )
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\n[INFO] Simulation gracefully paused by operator.")

if __name__ == "__main__":
    run_live_dashboard_simulation()