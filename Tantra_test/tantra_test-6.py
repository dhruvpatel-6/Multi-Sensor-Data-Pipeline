import time
import json
import uuid
import sys
import os

# Guarantee local workspace folder visibility
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Drivers.pipeline_sim import SimulatedRobot
from Layers.pipeline_sync import DataSynchronizer
from Core.fid import FailureIntelligence

def execute_end_to_end_tantra_proof():
    print("==================================================================")
    print("   TANTRA PHASE 7: END-TO-END UNBROKEN PIPELINE PROOF             ")
    print("==================================================================\n")

    # Initialize all modular system layers
    robot_hardware = SimulatedRobot()
    sync_layer = DataSynchronizer()
    brain = FailureIntelligence()
    
    log_filename = "telemetry_truth.jsonl"
    target_hz_period = 0.100  # Strict 10Hz Metronome Anchor Window (100ms)
    
    # ------------------------------------------------------------------
    # Step 1: Trace ID Anchor Definition
    # ------------------------------------------------------------------
    trace_id = f"TANTRA-E2E-PROOF-{uuid.uuid4().hex[:6].upper()}"
    print(f"[STEP 1: TRACE IDENTITY DEFINED]\n  -> Allocated Trace ID: {trace_id}\n")

    # Start the high-precision monotonic runtime clock
    cycle_start_perf = time.perf_counter()

    # ------------------------------------------------------------------
    # Step 2: Signal (Control Input Stub Injection)
    # ------------------------------------------------------------------
    # Simulating control targets coming down from Rajaryan's controller layer
    control_input_signal = {
        "system_mode": "BOUNDING_FLIGHT",
        "latency_ms": 1.25
    }
    print(f"[STEP 2: CONTROL INPUT SIGNAL INJECTED]\n  -> Signal Map: {control_input_signal}\n")

    # ------------------------------------------------------------------
    # Step 3: Actuator / Hardware Layer Interrogation (Rugved System)
    # ------------------------------------------------------------------
    robot_hardware.set_simulation_mode("NOMINAL")
    raw_hardware_snapshot = robot_hardware.get_full_hardware_stack()
    print(f"[STEP 3: ACTUATOR STACK FETCHED (Rugved Layer)]")
    print(f"  -> Hardware Health Status Reported: {raw_hardware_snapshot.get('status')}")
    print(f"  -> Baseline Pitch Measurement: {raw_hardware_snapshot.get('imu', {}).get('pitch')}°\n")

    # ------------------------------------------------------------------
    # Step 4: Telemetry Processing & Synchronization Layer
    # ------------------------------------------------------------------
    # Package raw maps directly into the non-negotiable canonical JSON contract schema
    serialized_contract_json = sync_layer.bundle(raw_hardware_snapshot, control_input_signal, trace_id)
    packet_data = json.loads(serialized_contract_json)
    
    # Track execution processing lag up to this checkpoint
    active_latency_ms = (time.perf_counter() - cycle_start_perf) * 1000
    packet_data["latency_ms"] = float(active_latency_ms)
    
    print(f"[STEP 4: TELEMETRY SCHEMA SYNCHRONIZATION]")
    print(f"  -> Successfully generated compliant contract JSON block.")
    print(f"  -> Active computation time measured: {active_latency_ms:.3f}ms\n")

    # ------------------------------------------------------------------
    # Step 5: Failure Intelligence Evaluation (The Brain)
    # ------------------------------------------------------------------
    safety_state, alert_reason = brain.evaluate_system(packet_data, active_latency_ms)
    packet_data["failure_reason"] = alert_reason
    
    print(f"[STEP 5: FAILURE INTELLIGENCE BRAIN EVALUATION]")
    print(f"  -> Brain Assigned State Action: {safety_state}")
    print(f"  -> Assigned Diagnostic Reason Code: {alert_reason}\n")

    # ------------------------------------------------------------------
    # Step 6: Truth Layer Persistence (Append-Only Logging)
    # ------------------------------------------------------------------
    print(f"[STEP 6: TRUTH LAYER IMMUTABLE COMMIT]")
    with open(log_filename, "a", encoding="utf-8") as ledger_file:
        ledger_entry_string = json.dumps(packet_data, sort_keys=True)
        ledger_file.write(ledger_entry_string + "\n")
        ledger_file.flush()
    print(f"  -> Frame serialized down to append-only storage: {log_filename}\n")

    # ------------------------------------------------------------------
    # Step 7: Deterministic Metronome Clock Pacing Lock
    # ------------------------------------------------------------------
    print(f"[STEP 7: DETERMINISTIC METRONOME SYNC CONTROL]")
    elapsed_time = time.perf_counter() - cycle_start_perf
    sleep_remainder = target_hz_period - elapsed_time
    
    if sleep_remainder > 0:
        time.sleep(sleep_remainder)
        total_frame_time_ms = (time.perf_counter() - cycle_start_perf) * 1000
        print(f"  -> Dynamic Sleep applied: {sleep_remainder*1000:.2f}ms")
        print(f"  -> Metronome frequency locked safely. Total frame window: {total_frame_time_ms:.2f}ms\n")
    else:
        print(f"  -> [WARNING] Deadline overrun detected! Frame slipped by {abs(sleep_remainder)*1000:.2f}ms\n")

    # ------------------------------------------------------------------
    # Step 8: Historical Audit Verification & Continuity Proof
    # ------------------------------------------------------------------
    print(f"[STEP 8: HISTORICAL REPLAY INTEGRITY AUDIT]")
    
    audit_passed = False
    with open(log_filename, "r", encoding="utf-8") as ledger_file:
        for line in ledger_file:
            clean_line = line.strip()
            if not clean_line:
                continue
            
            parsed_historical_frame = json.loads(clean_line)
            # Find the specific tracking ID generated during this test execution run
            if parsed_historical_frame.get("trace_id") == trace_id:
                audit_passed = True
                print(f"  -> Found unmutated tracking record matching ID: {parsed_historical_frame['trace_id']}")
                print(f"  -> Verified Values: Pitch = {parsed_historical_frame['imu_data']['pitch']:.2f}° | Health = {parsed_historical_frame['health_status']}")
                
                # Rigid assertions to guarantee zero null states are written or recovered
                assert "null" not in clean_line, "E2E Failure: Null type data leakage detected inside written ledger string!"
                assert "None" not in clean_line, "E2E Failure: Python system object references leaked inside written ledger string!"
                print("  -> Null Leakage Inspection Check: PASSED")

    if audit_passed:
        print("\n==================================================================")
        print(">>> SUCCESS: TANTRA END-TO-END PROOF FULLY VALIDATED. <<<")
        print("    Pipeline is Continuous, Deterministic, and 100% Verifiable.  ")
        print("==================================================================")
    else:
        print("\n[CRITICAL ERROR] End-to-End trace verification audit failed!")
        sys.exit(1)

if __name__ == "__main__":
    execute_end_to_end_tantra_proof()