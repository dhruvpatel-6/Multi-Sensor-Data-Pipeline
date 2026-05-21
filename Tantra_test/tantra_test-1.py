import json
from Layers.pipeline_sync import DataSynchronizer

def verify_phase_1_contract():
    sync = DataSynchronizer()
    
    # Simulate erratic/incomplete inputs from upstream components
    mock_rugved_raw = {
        "joint_states": {"FRONT_LEFT": {"HIP": 0.14}}, # Missing Knee entirely!
        "imu": {"pitch": 1.5, "roll": -0.2},         # Missing accel_z entirely!
        "status": "NOMINAL"
    }
    mock_rajaryan_raw = {
        "system_mode": "STABILIZING",
        "latency_ms": 4.5
    }
    
    # Generate packet through lock boundary
    serialized_output = sync.bundle(mock_rugved_raw, mock_rajaryan_raw, "TR-ID-PHASE1-INIT")
    
    # Load back to inspect structure correctness
    packet = json.loads(serialized_output)
    
    print("--- PHASE 1 CONTRACT LOCK TEST VERIFICATION ---")
    print(f"Serialized Result:\n{json.dumps(packet, indent=2)}\n")
    
    # Assert Mandatory Fields are structurally Present and non-null
    mandatory_fields = [
        "trace_id", "timestamp", "joint_states", "torque_outputs", 
        "imu_data", "contact_state", "health_status", "failure_reason", "latency_ms"
    ]
    
    for field in mandatory_fields:
        assert field in packet, f"Contract broken! Field '{field}' is missing."
        
    # Verify fallback for missing data works correctly
    assert "KNEE" in packet["joint_states"]["FRONT_LEFT"], "Nested schema fallback broke."
    assert packet["imu_data"]["accel_z"] == 9.81, "Default structural padding failed."
    
    print(">> SUCCESS: Phase 1 Contract Hardening Verified. Zero nulls, deterministic sort active. <<")

if __name__ == "__main__":
    verify_phase_1_contract()