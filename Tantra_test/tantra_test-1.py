# Tantra_test/tantra_test_1.py
# Phase 1 Schema Validation Driver — Hardened Convergence Task

import sys
import os
import json

# Path routing visibility anchor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Layers.pipeline_sync import DataSynchronizer

def test_phase_1_contract_lock():
    print("==================================================================")
    print(" RUNNING PHASE 1: CANONICAL CONTRACT LOCK SCHEMA HARDENING         ")
    print("==================================================================")
    
    sync = DataSynchronizer()
    trace_anchor = "TANTRA-TRACE-PHASE-1-LOCK"
    
    # Test Scenario: Input stream missing critical hip/knee nested subkeys
    malformed_hardware_snapshot = {
        "joint_states": {"hip": 0.45},  # Knee missing completely
        "imu_data": {"pitch": -1.2},     # Roll and Accel_z missing completely
        "health_status": "NOMINAL",
        "failure_reason": "NONE",
        "latency_ms": 1.45
    }
    mock_control_input = {"system_mode": "BOUNDING_FLIGHT"}

    # Execute the Schema Sync Operation passing all 3 convergence parameters
    json_contract_output = sync.bundle(malformed_hardware_snapshot, mock_control_input, trace_anchor)
    parsed_payload = json.loads(json_contract_output)

    print("\n[SUCCESS] Deterministic JSON Contract Generated Successfully.")
    print(json.dumps(parsed_payload, indent=2))
    
    # Strict Assertions ensuring explicit structure requirements are met
    print("\nPerforming Contract Structural Checks...")
    assert "trace_id" in parsed_payload, "Contract Breach: Missing trace_id field!"
    assert "timestamp" in parsed_payload, "Contract Breach: Missing timestamp field!"
    assert "knee" in parsed_payload["joint_states"], "Contract Breach: Missing fallback subkey validation for knee!"
    assert "accel_z" in parsed_payload["imu_data"], "Contract Breach: Missing fallback subkey validation for accel_z!"
    assert "contact_state" in parsed_payload, "Contract Breach: Missing contact_state field!"
    assert "null" not in json_contract_output, "Contract Breach: Fatal null type leakage inside data packet string!"
    
    print("-> ALL SCHEMA CONSTRAINTS VERIFIED: PASSED")
    print("==================================================================")

if __name__ == "__main__":
    test_phase_1_contract_lock()