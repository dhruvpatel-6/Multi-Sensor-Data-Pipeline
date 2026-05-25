import time
import json
import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Drivers.pipeline_sim import SimulatedRobot
from Layers.pipeline_sync import DataSynchronizer
from Core.fid import FailureIntelligence

def execute_logging_session():
    print("==================================================")
    print("  TANTRA TRUTH LAYER: LIVE LEDGER LOGGER ENGINE   ")
    print("==================================================\n")

    robot_hardware = SimulatedRobot()
    sync_layer = DataSynchronizer()
    brain = FailureIntelligence()

    rajaryan_stub = {"system_mode": "LEDGER_FLIGHT", "latency_ms": 1.4}
    log_filename = "telemetry_truth.jsonl"

    # Refresh ledger instance for clean session verification
    if os.path.exists(log_filename):
        os.remove(log_filename)

    target_hz_period = 0.100  # Strict 10Hz target frequency pacing (100ms)
    session_sequence = ["NOMINAL", "NOMINAL", "GHOST_DIVE", "NOMINAL"]

    print(f"[INIT] Opening append-only file handler: {log_filename}")
    
    with open(log_filename, "a", encoding="utf-8") as ledger_file:
        for cycle, mode in enumerate(session_sequence):
            cycle_start = time.perf_counter()
            
            # Phase 3 Rule: Entry point boundary trace assignment
            trace_id = f"TR-LEDGER-{uuid.uuid4().hex[:6].upper()}"

            # Simulate hardware changes
            robot_hardware.set_simulation_mode(mode)
            raw_hw = robot_hardware.get_full_hardware_stack()

            # Process through the canonical contract schema
            serialized_packet = sync_layer.bundle(raw_hw, rajaryan_stub, trace_id)
            packet = json.loads(serialized_packet)

            # Capture accurate loop latency metrics 
            execution_latency_ms = (time.perf_counter() - cycle_start) * 1000
            packet["latency_ms"] = float(execution_latency_ms)
            
            # Pass to failure intelligence to isolate failures natively
            safety_state, alert_reason = brain.evaluate_system(packet, execution_latency_ms)
            packet["failure_reason"] = alert_reason

            # APPEND-ONLY WRITE: Output full robot_state with sorted keys for predictability
            final_log_string = json.dumps(packet, sort_keys=True)
            ledger_file.write(final_log_string + "\n")
            ledger_file.flush()  # Push buffer blocks directly onto storage space

            print(f"[{trace_id}] Committed Cycle {cycle} | Mode: {mode} -> Action: {safety_state}")

            # 10Hz Metronome control
            elapsed = time.perf_counter() - cycle_start
            sleep_buffer = target_hz_period - elapsed
            if sleep_buffer > 0:
                time.sleep(sleep_buffer)

    print(f"\n>>> SUCCESS: Session finalized. Telemetry written to {log_filename} <<<")

if __name__ == "__main__":
    execute_logging_session()