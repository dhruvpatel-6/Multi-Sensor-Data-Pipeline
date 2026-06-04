import json
from Hardware.hardware_bridge import QuadrupedHardwareBridge

def execute_hal_audit_suite():
    print("="*60)
    print("[+] CRITICAL SPRINT: HAL UPGRADE RUNNER")
    print("="*60)
    
    hal = QuadrupedHardwareBridge()
    commanded_torques = [12.0, 15.5, 11.2, 14.0]
    
    # 1. Nominal Mode Test
    print("\n[+] Executing Operational Scenario 1: Nominal Loop Mode...")
    nominal_res = hal.process_hardware_step(commanded_torques, "NOMINAL")
    print(f"[-] Frame ID: {nominal_res['trace_id']} | Health: {nominal_res['health_status']}")
    print(f"[-] Actuator Bus Metrics: {nominal_res['actuation_state']['bus_health']}")

    # 2. Sensor Noise Test
    print("\n[+] Executing Operational Scenario 2: Injecting Sensor Noise...")
    noise_res = hal.process_hardware_step(commanded_torques, "SENSOR_NOISE")
    print(f"[-] Perturbed Kinematic Hip Outputs: {noise_res['locomotion_state']['hip_angles']}")

    # 3. Timing Jitter Test
    print("\n[+] Executing Operational Scenario 3: Inducing Timing Jitter Spikes...")
    jitter_res = hal.process_hardware_step(commanded_torques, "TIMING_JITTER")
    print(f"[-] Tracked Processing Delay: {jitter_res['loop_latency_ms']} ms | Alert Tag: {jitter_res['system_health']['timing_status']}")

    # 4. Missing Packets Test
    print("\n[+] Executing Operational Scenario 4: Simulating Dropped / Missing Packets...")
    missing_res = hal.process_hardware_step(commanded_torques, "MISSING_PACKETS")
    print(f"[-] Bus Node Status: {missing_res['system_health']['watchdog_status']} | Global System Posture: {missing_res['health_status']}")

    # 5. Thermal Evolution Test
    print("\n[+] Executing Operational Scenario 5: Running Thermal Evolution Profile...")
    extreme_torques = [40.0, 42.5, 38.0, 41.2]
    # Pump the execution loop steps to watch systemic heat calculation acceleration
    for step in range(3):
        thermal_res = hal.process_hardware_step(extreme_torques, "THERMAL_EVOLUTION")
    print(f"[-] Winding Temps Escalated to: {thermal_res['actuation_state']['thermal_state']} °C")

    # 6. Partial Actuator Degradation Test
    print("\n[+] Executing Operational Scenario 6: Actuator Winding Partial Degradation...")
    high_torque_demand = [30.0, 30.0, 30.0, 30.0]
    degraded_res = hal.process_hardware_step(high_torque_demand, "PARTIAL_ACTUATOR_DEGRADATION")
    print(f"[-] Target Torque Demand: 30.0 Nm -> Physical Winding Clipped At: {degraded_res['actuation_state']['joint_torque']}")
    print(f"[-] Driver Feedback Payload Flag: {degraded_res['actuation_state']['driver_status']}")

    # 7. Recoverable Faults Test
    print("\n[+] Executing Operational Scenario 7: Intercepting Recoverable Fault Arrays...")
    rec_res = hal.process_hardware_step(commanded_torques, "RECOVERABLE_FAULTS")
    print(f"[-] Non-Fatal Bus Posture: {rec_res['actuation_state']['bus_health']} | Recovery Routine Status: {rec_res['control_state']['recovery_state']}")

    # 8. Critical Faults Test
    print("\n[+] Executing Operational Scenario 8: Forcing Critical System Failure Crashes...")
    crit_res = hal.process_hardware_step(commanded_torques, "CRITICAL_FAULTS")
    print(f"[-] Global Health Matrix Tripped: {crit_res['health_status']}")
    print(f"[-] Watchdog Status Logging: {crit_res['system_health']['watchdog_status']} | Protective Action: {crit_res['control_state']['recovery_state']}")
    print("="*60)

if __name__ == "__main__":
    execute_hal_audit_suite()