import sys
import os

# Ensure the root directory is explicitly in Python's path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import json
    from Drivers.pipeline_sim import SimulatedRobot
    from Layers.pipeline_sync import DataSynchronizer
    print("[INIT SUCCESS] Core telemetry components imported correctly.")
except ImportError as e:
    print(f"[CRITICAL ERROR] Failed to import modules: {e}")
    print("Ensure you have empty '__init__.py' files inside your 'Drivers/' and 'Layers/' directories.")
    sys.exit(1)

def verify_phase_2_integration():
    print("\n==================================================")
    print("   TANTRA PHASE 2: INPUT INTEGRATION TEST BENCH   ")
    print("==================================================")

    # 1. Instantiate the upstream blocks
    try:
        robot_hardware = SimulatedRobot()
        sync_layer = DataSynchronizer()
        print("[1/3] Hardware simulator and Synchronizer initialized.")
    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        return

    # 2. Simulate Rajaryan's Control Engine Engine Stub Input
    rajaryan_control_stub = {
        "target_state": "NOMINAL_WALK",
        "system_mode": "BOUNDING",
        "latency_ms": 5.40
    }
    
    # 3. Execute Nominal Flow Ingestion
    try:
        print("[2/3] Fetching upstream data stream from Rugved's actuator stack...")
        raw_hw_data = robot_hardware.get_full_hardware_stack()
        
        # Match your pipeline_sync.py exact parameter signature: (rugved_hardware, rajaryan_control, upstream_trace_id)
        serialized_packet = sync_layer.bundle(raw_hw_data, rajaryan_control_stub, "TRACE-PHASE2-NOMINAL")
        packet = json.loads(serialized_packet)
        
        print("\n>>> [SUCCESS] OUTPUT CAPTURED FROM TRUTH CONTRACT LOCK <<<")
        print(f"    Trace ID:       {packet.get('trace_id')}")
        print(f"    System Mode:    {packet.get('system_mode')}")
        print(f"    Health Status:  {packet.get('health_status')}")
        print(f"    Pitch Angle:    {packet.get('imu_data', {}).get('pitch'):.4f}°")
        print(f"    Joint Status:   FRONT_LEFT HIP = {packet.get('joint_states', {}).get('FRONT_LEFT', {}).get('HIP')} rad")
    except Exception as e:
        print(f"[CRITICAL PIPELINE ERROR] Nominal bundle generation failed: {e}")
        return

    # 4. Execute Fault Injection Flow Verification
    try:
        print("\n[3/3] Injecting boundary fault 'GHOST_DIVE' into actuator line...")
        robot_hardware.set_simulation_mode("GHOST_DIVE")
        corrupt_hw_data = robot_hardware.get_full_hardware_stack()
        
        failed_serialized = sync_layer.bundle(corrupt_hw_data, rajaryan_control_stub, "TRACE-PHASE2-FAULT")
        failed_packet = json.loads(failed_serialized)
        
        print("\n>>> [SUCCESS] FAULT BOUNDARY CAPTURED IN CONTEXT LOCK <<<")
        print(f"    Trace ID:       {failed_packet.get('trace_id')}")
        print(f"    Health Status:  {failed_packet.get('health_status')}")
        print(f"    Failure Reason: {failed_packet.get('failure_reason')}")
        print(f"    Corrupt Pitch:  {failed_packet.get('imu_data', {}).get('pitch'):.1f}")
        
        # Confirm integrity assertions match structural expectations
        assert failed_packet['health_status'] == "CRITICAL", "Fault state tracking dropped!"
        print("\n>> VERIFICATION COMPLETE: Phase 2 Contract is perfectly operational. <<")
    except Exception as e:
        print(f"[CRITICAL PIPELINE ERROR] Fault handling mapping failed: {e}")

if __name__ == "__main__":
    verify_phase_2_integration()