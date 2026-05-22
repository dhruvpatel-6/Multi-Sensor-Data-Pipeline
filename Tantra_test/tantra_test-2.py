# Tantra_test/tantra_test_2.py
# Phase 2 Upstream Input Integration Verification Test

import sys
import os
import json

# Path routing visibility anchor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Drivers.pipeline_sim import SimulatedRobot
from Telemetry.main_control_loop import TantraTelemetryEngine

def test_phase_2_upstream_integration():
    print("==================================================================")
    print(" RUNNING PHASE 2: REAL UPSTREAM BOUNDARY INTEGRATION TEST        ")
    print("==================================================================")
    
    # Initialize separate components representing the independent TANTRA tracking layers
    rugved_hardware_source = SimulatedRobot()
    telemetry_engine = TantraTelemetryEngine()
    
    trace_anchor = "TANTRA-TRACE-CONVERGENCE-P2-VALIDATION"

    # 1. Simulate Input Source A: Rugved Actuator Control System (Joints + Torques)
    print("[BOUNDARY] Polling Rugved Actuator Control System Registers...")
    rugved_packet = rugved_hardware_source.get_full_hardware_stack()
    print(f" -> Received Joint States: {rugved_packet['joint_states']}")
    print(f" -> Received Torque Outputs: {rugved_packet['torque_outputs']}")

    # 2. Simulate Input Source B: Rajaryan Control Layer (Target state + system mode)
    print("\n[BOUNDARY] Intercepting Rajaryan Control Engine Setpoints...")
    rajaryan_packet = {
        "target_state": {"position_x": 0.0, "velocity_z": 1.2},
        "system_mode": "BOUNDING_FLIGHT"
    }
    print(f" -> Active System Mode: {rajaryan_packet['system_mode']}")

    # 3. Process integration convergence cycle across the boundaries
    print("\n[PROCESSING] Passing multi-source boundary streams to Telemetry Engine...")
    json_output = telemetry_engine.execute_integration_cycle(
        rugved_actuator_packet=rugved_packet,
        rajaryan_control_packet=rajaryan_packet,
        upstream_trace_id=trace_anchor
    )
    
    parsed_contract = json.loads(json_output)
    print("\n[SUCCESS] Unified Canonical Telemetry JSON Frame Output Locked:")
    print(json.dumps(parsed_contract, indent=2))

    # Assertions validating absolute multi-source parameter preservation
    print("\nAuditing Integrated Field Constraints...")
    assert parsed_contract["trace_id"] == trace_anchor, "Integration Error: Trace key mutated!"
    assert "hip" in parsed_contract["joint_states"], "Integration Error: Rugved joint_states data lost!"
    assert "hip" in parsed_contract["torque_outputs"], "Integration Error: Rugved torque_outputs data lost!"
    assert "pitch" in parsed_contract["imu_data"], "Integration Error: Rugved IMU tracking data lost!"
    
    print("-> ALL UPSTREAM INTEGRATION CHECKS: PASSED")
    print("==================================================================")

if __name__ == "__main__":
    test_phase_2_upstream_integration()