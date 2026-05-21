# test_phase_4.py
# Phase 4 Verification: 10Hz Deterministic Metronome Clock

import time
import json
import uuid
import sys
import os

# Guarantee local workspace visibility
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Drivers.pipeline_sim import SimulatedRobot
from Layers.pipeline_sync import DataSynchronizer
from Core.fid import FailureIntelligence

def verify_phase_4_deterministic_loop():
    print("==================================================")
    print("  TANTRA VERIFICATION BENCH: PHASE 4 10HZ CLOCK   ")
    print("==================================================\n")

    robot_hardware = SimulatedRobot()
    sync_layer = DataSynchronizer()
    brain = FailureIntelligence()

    # Fixed configuration boundaries
    rajaryan_control_stub = {"system_mode": "TANTRA_METRONOME", "latency_ms": 1.8}
    total_cycles = 6
    target_hz_period = 0.100  # Exactly 100ms target execution budget per frame

    print(f"Starting deterministic tracking loop. Target Rate: 10Hz ({target_hz_period*1000}ms loop interval)")

    for cycle in range(total_cycles):
        # Anchor the high-resolution start time step
        cycle_start_perf = time.perf_counter()
        
        # Phase 3 requirement: Trace continuity verification
        trace_id = f"TR-HZ4-{uuid.uuid4().hex[:6].upper()}"

        # Inject a real timing failure spike on Cycle 3
        if cycle == 3:
            print("\n[CLOCK INJECT] Simulating an unexpected 135ms thread execution blocking stall...")
            time.sleep(0.135)  # Forcefully slip past the 120ms max threshold limit
        
        # 1. FETCH (Input Integration Boundary)
        raw_hw_data = robot_hardware.get_full_hardware_stack()

        # 2. BUNDLE (Enforce Phase 1 Schema Contract)
        serialized_packet = sync_layer.bundle(raw_hw_data, rajaryan_control_stub, trace_id)
        packet = json.loads(serialized_packet)

        # 3. MEASURE TIMING & EVALUATE METRIC DRIFT
        # Compute exact active execution delay time up to this point
        execution_latency_ms = (time.perf_counter() - cycle_start_perf) * 1000
        
        # Insert high-precision latency measurement directly back into contract payload
        packet["latency_ms"] = float(execution_latency_ms)

        # Pass payload packet into safety engine to monitor structural budget alignment
        safety_state, alert_reason = brain.evaluate_system(packet, execution_latency_ms)

        print(f"[{trace_id}] Cycle {cycle} | Active Processing: {execution_latency_ms:.2f}ms | Safety State: {safety_state} ({alert_reason})")

        # 4. MONOTONIC DYNAMIC METRONOME COMPENSATION
        # Calculate exactly how much remainder sleep buffer is needed to complete the 100ms cycle
        elapsed_time = time.perf_counter() - cycle_start_perf
        sleep_buffer = target_hz_period - elapsed_time

        if sleep_buffer > 0:
            time.sleep(sleep_buffer)
            total_cycle_time = (time.perf_counter() - cycle_start_perf) * 1000
            print(f"     ↳ Dynamic Sleep applied: {sleep_buffer*1000:.1f}ms | Total frame window: {total_cycle_time:.1f}ms")
        else:
            print(f"     ↳ [TIMING OVERRUN WARNING] Cycle dropped deadline budget by {abs(sleep_buffer)*1000:.1f}ms!")
            
            # Assert that the system correctly caught and reported the timing violation on Cycle 3
            if cycle == 3:
                assert safety_state == "DEGRADED" and alert_reason == "LOOP_CLOCK_OVERRUN", "Failure logic let a loop overrun slip undetected!"

    print("\n>>> SUCCESS: Phase 4 Deterministic Clock Loop Verified. Dynamic 10Hz synchronization is stable. <<<")

if __name__ == "__main__":
    verify_phase_4_deterministic_loop() 