# Tantra_test/tantra_test_6.py
# Phase 6 — Truth Layer Logging & Replay Validation Suite

import sys
import os
import json
import time

# Ensure nested multi-layer folder structures discover parent imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from Telemetry.main_control_loop import TantraTelemetryEngine
from Telemetry.replay_telemetry import TantraTruthReplayEngine

def run_phase_6_truth_layer_tests():
    print("==================================================================")
    print(" RUNNING PHASE 6: LOGGING Ledger AND CADENCE REPLAY AUDIT         ")
    print("==================================================================")

    test_log_path = "Tantra_logs/telemetry_truth.jsonl"
    
    # Clean workspace from older cache logs to ensure clean tracking evaluation
    if os.path.exists(test_log_path):
        os.remove(test_log_path)

    engine = TantraTelemetryEngine(output_filepath=test_log_path)
    replay = TantraTruthReplayEngine(log_filepath=test_log_path)

    # 1. Seed historical logs using the primary execution integration loops
    print("[STEP 1] Generating fresh contract logs via integrated execution cycle...")
    seeded_traces = []
    
    for idx in range(5):
        trace_token = f"TANTRA-P6-TRUTH-LOG-00{idx}"
        seeded_traces.append(trace_token)
        
        # Build mock mechatronic states
        hw_packet = {
            "joint_states": {"hip": 0.12 * (idx + 1), "knee": -0.34},
            "imu_data": {"accel_z": 9.81, "pitch": 0.0, "roll": 1.2},
            "torque_outputs": {"FRONT_LEFT": 1.25}
        }
        control_packet = {"system_mode": "TRUTH_SEEDING", "target_state": {}}
        
        engine.execute_integration_cycle(
            rugved_actuator_packet=hw_packet,
            rajaryan_control_packet=control_packet,
            upstream_trace_id=trace_token,
            execution_latency_ms=1.5
        )

    # Verify log output existence
    assert os.path.exists(test_log_path), "Validation Failure: Append-only ledger file not created!"
    
    # 2. Fire the replay engine tracking execution parameters
    print("\n[STEP 2] Launching playback framework to monitor reproduction cadence...")
    start_time = time.monotonic()
    
    reproduced_count = replay.execute_replay(target_hz=10.0)
    
    total_playback_duration = (time.monotonic() - start_time) * 1000.0
    expected_duration = (reproduced_count - 1) * 100.0  # ~100ms intervals between frames

    print(f"\n[TIMING ANALYSIS]")
    print(f" -> Total Frames Transacted: {reproduced_count}")
    print(f" -> Measured Playback Wall-Time: {total_playback_duration:.2f} ms")
    print(f" -> Mathematical Baseline Expected: {expected_duration:.2f} ms")

    # 3. Assert structural integrity and trace validation requirements
    assert reproduced_count == len(seeded_traces), "Validation Failure: Replay missed ledger lines!"
    
    # Confirm timing stability bounds match OS scheduling intervals safely (~10Hz)
    assert total_playback_duration >= expected_duration - 50.0, "Validation Failure: Replay pace ran too fast/drifted!"

    print("\n==================================================================")
    print(" -> TRUTH LAYER REPLAY VERIFICATION: VALID AND PASSED             ")
    print("==================================================================")

if __name__ == "__main__":
    run_phase_6_truth_layer_tests()