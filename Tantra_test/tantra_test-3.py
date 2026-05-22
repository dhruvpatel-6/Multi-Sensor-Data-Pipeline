import sys
import os
import json

# Ensure parent directory exposure for package resolution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Drivers.pipeline_sim import SimulatedRobot
from Telemetry.main_control_loop import TantraTelemetryEngine

def test_phase_3_trace_propagation():
    print("==================================================================")
    print(" RUNNING PHASE 3: NON-NEGOTIABLE TRACE PROPAGATION VALIDATION    ")
    print("==================================================================")
    
    # 1. Establish the Immutable Target Trace Token Anchor
    TARGET_TRACE_ID = "TANTRA-PROPAGATION-TOKEN-99X88"
    print(f"[STEP 1: INPUT BOUNDARY] Originating Trace ID Token: {TARGET_TRACE_ID}")
    
    # Initialize component blocks
    robot = SimulatedRobot()
    log_file_path = "Tantra_logs/telemetry_truth.jsonl"
    telemetry_engine = TantraTelemetryEngine(output_filepath=log_file_path)
    
    # Extract upstream sensor packets and mock control settings
    raw_hw = robot.get_full_hardware_stack()
    mock_control = {"system_mode": "BOUNDING_FLIGHT", "target_state": {}}
    
    # 2. Process data frame and write directly into the ledger database
    print("\n[STEP 2: PROCESSING] Pushing transaction through structural pipeline...")
    json_contract_output = telemetry_engine.execute_integration_cycle(
        rugved_actuator_packet=raw_hw,
        rajaryan_control_packet=mock_control,
        upstream_trace_id=TARGET_TRACE_ID
    )
    
    parsed_contract = json.loads(json_contract_output)
    output_contract_trace = parsed_contract.get("trace_id")
    print(f" -> Output Schema Contract Emitted Trace: {output_contract_trace}")
    
    # Validation A: Check inside schema contract serialization layer
    assert output_contract_trace == TARGET_TRACE_ID, "CRITICAL ERROR: Trace ID mutated inside contract synchronization block!"
    print("[SUCCESS] Contract Layer Verification: Match Confirmed.")

    # 3. Replay and audit the written log entry line
    print("\n[STEP 3: TRUTH LAYER LOGS] Reading last appended line from ledger registry...")
    with open(log_file_path, "r", encoding="utf-8") as ledger:
        lines = ledger.readlines()
        last_recorded_line = lines[-1].strip()
        
    parsed_log_entry = json.loads(last_recorded_line)
    persisted_log_trace = parsed_log_entry.get("trace_id")
    print(f" -> Persisted Ledger File Written Trace:  {persisted_log_trace}")
    
    # Validation B: Check inside cold storage persistent logging layer
    assert persisted_log_trace == TARGET_TRACE_ID, "CRITICAL ERROR: Trace ID mutated inside append-only file writer!"
    print("[SUCCESS] Ledger Database Verification: Match Confirmed.")
    
    print("\n==================================================================")
    print(" VERIFICATION CONCLUSION: PASSED                                  ")
    print(f" Single trace [{TARGET_TRACE_ID}] successfully propagated across full flow!")
    print("==================================================================")

if __name__ == "__main__":
    test_phase_3_trace_propagation()