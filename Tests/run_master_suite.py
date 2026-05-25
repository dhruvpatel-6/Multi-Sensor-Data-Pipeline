# Tests/run_master_suite.py
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from Hardware.quadruped_hardware_bridge import QuadrupedHardwareBridge
from Telemetry.telemetry_orchestrator import QuadrupedTelemetryOrchestrator
from Telemetry.blackbox_replay import QuadrupedBlackboxReplay

def run_all_integration_phases():
    print("==================================================================")
    print(" EXECUTING ROBOTICS TELEMETRY MASTER PIPELINE SUITE              ")
    print("==================================================================")
    
    log_file = "Logs/quadruped_telemetry_truth.jsonl"
    if os.path.exists(log_file):
        os.remove(log_file)

    bridge = QuadrupedHardwareBridge()
    orchestrator = QuadrupedTelemetryOrchestrator(output_filepath=log_file)
    replay = QuadrupedBlackboxReplay(log_filepath=log_file)

    mock_control = {"system_mode": "INTEGRATION_SUITE_RUN", "target_state": {}}

    print("\n[RUNNING NOMINAL STACK]")
    bridge.set_simulation_mode("NOMINAL")
    orchestrator.execute_integration_cycle(bridge.get_full_hardware_stack(), mock_control, "TRACE-NOMINAL-01", 0.45)

    print("\n[RUNNING FAULT STACK: MISSING BUS DATA]")
    bridge.set_simulation_mode("FAULT_MISSING_DATA")
    orchestrator.execute_integration_cycle(bridge.get_full_hardware_stack(), mock_control, "TRACE-FAULT-BUS-TIMEOUT", 1.89)

    print("\n[RUNNING FAULT STACK: CORRUPT IMU SIGNAL]")
    bridge.set_simulation_mode("FAULT_CORRUPT_SENSOR")
    orchestrator.execute_integration_cycle(bridge.get_full_hardware_stack(), mock_control, "TRACE-FAULT-GHOST-DIVE", 0.92)

    total_replayed = replay.execute_replay(target_hz=10.0)
    assert total_replayed == 3
    
    print("\n==================================================================")
    print(" -> GLOBAL INTEGRATION VERIFICATION: ALL PIPELINE PHASES PASSED   ")
    print("==================================================================")

if __name__ == "__main__":
    run_all_integration_phases()
