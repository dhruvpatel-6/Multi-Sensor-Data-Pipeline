# Tantra_test/tantra_test_4.py
# Phase 4: Deterministic 10Hz Cadence Performance Verification Driver

import sys
import os
import time
import json

# Ensure parent path visibility for execution routing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Drivers.pipeline_sim import SimulatedRobot
from Telemetry.main_control_loop import TantraTelemetryEngine

def test_phase_4_realtime_frequency_lock():
    print("==================================================================")
    print(" RUNNING PHASE 4: DETERMINISTIC 10HZ REAL-TIME LOOP PERFORMANCE   ")
    print("==================================================================")
    
    robot = SimulatedRobot()
    telemetry_engine = TantraTelemetryEngine()
    
    TARGET_HZ = 10.0
    INTERVAL_SEC = 1.0 / TARGET_HZ  # Exactly 100.00 ms 
    
    print(f"[INFO] Initializing cadence track profile (10 consecutive cycles)...")
    
    execution_history = []
    next_interval_anchor = time.monotonic()
    current_latency = 0.0
    
    for cycle_idx in range(10):
        cycle_start = time.monotonic()
        execution_history.append(cycle_start)
        
        trace_token = f"TANTRA-P4-LOCK-TRACE-00{cycle_idx}"
        
        # Fetch data across mechatronic boundaries [cite: 31, 34]
        hw_packet = robot.get_full_hardware_stack()
        control_packet = {"system_mode": "CADENCE_LOCK", "target_state": {}}
        
        # Execute cycle [cite: 3]
        telemetry_engine.execute_integration_cycle(
            rugved_actuator_packet=hw_packet,
            rajaryan_control_packet=control_packet,
            upstream_trace_id=trace_token,
            execution_latency_ms=current_latency
        )
        
        # Update latency profiling metrics [cite: 50]
        current_latency = (time.monotonic() - cycle_start) * 1000.0
        
        # Anti-drift dynamic compensation sleep calculation [cite: 48]
        next_interval_anchor += INTERVAL_SEC
        sleep_remainder = next_interval_anchor - time.monotonic()
        
        if sleep_remainder > 0:
            time.sleep(sleep_remainder)
        else:
            next_interval_anchor = time.monotonic()

    print("\n[ANALYSIS] Calculating Metric Variations per Iteration Frame:")
    deltas_ms = []
    for idx in range(1, len(execution_history)):
        frame_delta = (execution_history[idx] - execution_history[idx - 1]) * 1000.0
        deltas_ms.append(frame_delta)
        print(f" -> Loop Delta Step {idx}: {frame_delta:.2f} ms (Target Baseline: 100.00 ms)")

    # Analyze total clock stability metrics 
    average_cadence_interval = sum(deltas_ms) / len(deltas_ms)
    print(f"\nAverage System Frequency Execution Speed: {average_cadence_interval:.2f} ms")
    
    # Enforce strict 10Hz bounds verification (allowing standard OS scheduling jitter bounds) [cite: 46, 51]
    assert 90.0 <= average_cadence_interval <= 110.0, f"Timing Contract Breached: Loop average fell out of deterministic bounds!"
    
    print("\n-> DETERMINISTIC FREQUENCY PERFORMANCE MATRIX: PASSED")
    print("==================================================================")

if __name__ == "__main__":
    test_phase_4_realtime_frequency_lock()