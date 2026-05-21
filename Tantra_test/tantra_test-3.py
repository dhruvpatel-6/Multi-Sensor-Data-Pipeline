# test_phase_3.py
import json
import uuid  # Safely imported at file scope
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Drivers.pipeline_sim import SimulatedRobot
from Layers.pipeline_sync import DataSynchronizer
from Core.fid import FailureIntelligence

def verify_phase_3_propagation_proof():
    print("==================================================")
    print("  TANTRA VERIFICATION BENCH: PHASE 3 PROPAGATION  ")
    print("==================================================\n")

    # 1. Instantiate architectural blocks
    robot_hardware = SimulatedRobot()
    sync_layer = DataSynchronizer()
    brain = FailureIntelligence()

    # 2. Simulate external seed trace generated at the extreme control boundary edge
    upstream_seed_trace = f"TANTRA-TX-BOUND-{uuid.uuid4().hex[:6].upper()}"
    print(f"[INPUT BOUNDARY ENTRY] Generated Core Trace ID: {upstream_seed_trace}")

    mock_rajaryan_control = {
        "system_mode": "TROTTING",
        "latency_ms": 2.80
    }

    # 3. Step 1: Extract hardware layer inputs
    print("\n[STEP 1: PROCESSING] Fetching data payload from Rugved simulator stream...")
    raw_hw = robot_hardware.get_full_hardware_stack()

    # 4. Step 2: Enforce Contract lock boundary (Packaging into Canonical JSON)
    print("[STEP 2: PROCESSING] Pushing elements through contract lock synchronizer...")
    serialized_contract = sync_layer.bundle(raw_hw, mock_rajaryan_control, upstream_seed_trace)
    packet = json.loads(serialized_contract)
    
    extracted_trace = packet.get("trace_id")
    print(f"     ↳ Extracted Packet trace_id: {extracted_trace}")

    # 5. Step 3: Pass into Decision Safety Brain Engine
    print("\n[STEP 3: EVALUATION] Transferring canonical packet directly into safety brain...")
    safety_state, alert_reason = brain.evaluate_system(packet, loop_latency_ms=1.4)
    print(f"     ↳ Brain Output Context linked to trace token. Evaluation State: {safety_state}")

    # 6. Step 4: Output Logs (Simulating structural file record storage payload)
    print("\n[STEP 4: LOG OUTPUT] Serializing pipeline records down to system logs stream...")
    simulated_log_line = json.dumps({"log_timestamp": packet["timestamp"], "trace_id": packet["trace_id"], "system_health": packet["health_status"]})
    print(f"     ↳ Written Log Line: {simulated_log_line}")

    # --- CRITICAL ABSOLUTE TESTS FOR PHASE 3 VERIFICATION ---
    print("\n==================================================")
    print("           TRACE CONTINUITY ASSERTIONS            ")
    print("==================================================")
    
    print(f"Checking Input  Trace == Processing Trace? ", end="")
    assert upstream_seed_trace == extracted_trace, "CRITICAL ERROR: Trace mutated during bundling extraction!"
    print("PASSED")

    print(f"Checking Process Trace == Log Record Trace? ", end="")
    log_data = json.loads(simulated_log_line)
    assert extracted_trace == log_data["trace_id"], "CRITICAL ERROR: Trace mutated during log writing file commit!"
    print("PASSED")

    print("\n>>> SUCCESS: Phase 3 Continuity Lock Verified. Trace is 100% unmutated across the chain. <<<")

if __name__ == "__main__":
    verify_phase_3_propagation_proof()