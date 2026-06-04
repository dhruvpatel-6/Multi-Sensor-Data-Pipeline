import json
import os
from jsonschema import validate, ValidationError

def run_contract_test():
    schema_path = "schema/canonical_telemetry_v3.json"
    
    if not os.path.exists(schema_path):
        print(f"[!] Critical Error: {schema_path} file is missing!")
        return

    with open(schema_path, "r") as f:
        master_schema = json.load(f)

    # Valid telemetry packet matching Phase F constraints completely
    valid_sample = {
        "timestamp": "2026-06-03T18:00:00.000Z",
        "trace_id": "TRC-2026-A1B2C3D4",
        "health_status": "NOMINAL",
        "loop_latency_ms": 3.84,
        "control_state": {"gait_mode": "TROTTING", "target_velocity": [1.0, 0.0, 0.0], "control_mode": "POSITION", "recovery_state": "INACTIVE"},
        "locomotion_state": {"hip_angles": [0.1, -0.1, 0.1, -0.1], "knee_angles": [0.6, 0.6, 0.6, 0.6], "foot_positions": [[0,0,0],[0,0,0],[0,0,0],[0,0,0]], "support_polygon_state": "STABLE_QUAD", "stability_margin": 92.4},
        "terrain_state": {"terrain_type": "CONCRETE_DRY", "slip_probability": 0.02, "traction_state": "OPTIMAL", "incline_estimate": 0.0},
        "actuation_state": {"joint_torque": [12.4, 11.8, 12.1, 12.5], "driver_status": "OPERATIONAL", "bus_health": "HEALTHY", "thermal_state": [42.0, 41.5, 43.0, 42.2]},
        "system_health": {"watchdog_status": "HEARTBEAT_OK", "timing_status": "DETERMINISTIC", "schema_status": "VALIDATED", "replay_status": "LIVE_STREAM"}
    }

    # Malformed packet violating additionalProperties constraint
    invalid_sample = json.loads(json.dumps(valid_sample))
    invalid_sample["custom_unauthorized_field"] = "Breaking Contract Duplication Locks"

    print("[+] Test 1: Validating Compliant Multi-Builder Structural Frame...")
    try:
        validate(instance=valid_sample, schema=master_schema)
        print("[-] Result: PASSED. Frame complies cleanly with Unified Canonical Truth.")
    except ValidationError as e:
        print(f"[!] Result: FAILED. Schema rejected valid block: {e.message}")

    print("\n[+] Test 2: Injecting Unauthorized Branch Extension Frame...")
    try:
        validate(instance=invalid_sample, schema=master_schema)
        print("[!] Result: FAILED. Schema failed to catch contract duplication inflation.")
    except ValidationError:
        print("[-] Result: PASSED. Schema successfully blocked unauthorized additions and kept data contract pristine.")

if __name__ == "__main__":
    run_contract_test()