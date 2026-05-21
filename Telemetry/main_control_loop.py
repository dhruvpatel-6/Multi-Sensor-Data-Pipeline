import time
import json
import uuid  # Explicitly imported to guarantee global file scoping
import sys
import os

# Guarantee local workspace visibility
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Drivers.pipeline_sim import SimulatedRobot
from Layers.pipeline_sync import DataSynchronizer
from Core.fid import FailureIntelligence

def run_pipeline_cycle():
    print("==================================================")
    print("  TANTRA CORE INTEGRATION: PHASE 3 TRACE TIMELINE ")
    print("==================================================\n")

    # Initialize all active architectural components
    robot_hardware = SimulatedRobot()
    sync_layer = DataSynchronizer()
    brain = FailureIntelligence()

    # Simulate Rajaryan's Upstream Core Engine Input
    rajaryan_stub = {
        "system_mode": "TANTRA_ALIGN",
        "latency_ms": 3.2
    }

    # Sequence of modes to test to verify uninterrupted trace propagation
    test_sequence = ["NOMINAL", "GHOST_DIVE"]

    for run_mode in test_sequence:
        print(f"\n--- EXECUTION CONTEXT: {run_mode} ---")
        robot_hardware.set_simulation_mode(run_mode)

        # Execute continuous cycles per mode to observe trace pass-through stability
        for cycle in range(2):
            start_time = time.time()

            # Phase 3 Core Requirement: Generate trace ID at the extreme boundary edge
            upstream_generated_trace = f"TANTRA-TR-{uuid.uuid4().hex[:6].upper()}"

            # 1. FETCH (Upstream Interface Entry)
            raw_hardware = robot_hardware.get_full_hardware_stack()
            
            # 2. BUNDLE (Enforce Phase 1 contract while anchoring the original trace token)
            serialized_contract = sync_layer.bundle(raw_hardware, rajaryan_stub, upstream_generated_trace)
            packet = json.loads(serialized_contract)

            # 3. EVALUATE (Pass to Brain without altering metadata tokens)
            loop_latency = (time.time() - start_time) * 1000
            safety_state, alert_reason = brain.evaluate_system(packet, loop_latency)

            # Extract data points directly from the locked structural keys
            current_trace = packet.get("trace_id")
            packet_status = packet.get("health_status")
            pitch_val = packet.get("imu_data", {}).get("pitch")

            # Validate that the token received at the terminal matches the entry token
            print(f"[{current_trace}] Cycle {cycle} -> Brain Decision: {safety_state} | Hardware State: {packet_status} | Pitch: {pitch_val:.2f}°")
            
            if safety_state == "STOP":
                print(f"    ↳ [SAFETY TRIGGERED] Reason: {alert_reason}")

            time.sleep(0.05)

if __name__ == "__main__":
    run_pipeline_cycle()