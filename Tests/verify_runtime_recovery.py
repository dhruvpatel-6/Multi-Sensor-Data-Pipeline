import json
from metrics.runtime_monitor import DeterministicRuntimeMonitor

def run_runtime_recovery_audit():
    print("="*70)
    print("[+] PHASE H RUNTIME MONITOR")
    print("="*70)
    
    # Initialize the engine targeting a strict 4.0 ms processing deadline
    monitor = DeterministicRuntimeMonitor(target_deadline_ms=4.0)
    
    # Scenario 1: Highly compliant loop cycle
    print("\n[+] Testing Execution Cycle 1: Nominial Compliant Frame...")
    log_1 = monitor.audit_loop_step(actual_latency_ms=3.74)
    print(json.dumps(log_1, indent=2))
    
    # Scenario 2: Moderate Jitter breach (OS/Bus congestion)
    print("\n[+] Testing Execution Cycle 2: Congested CAN-Bus Jitter Spike...")
    log_2 = monitor.audit_loop_step(actual_latency_ms=9.15)
    print(json.dumps(log_2, indent=2))
    
    # Scenario 3: Severe Thread Lock triggering aggressive mitigation
    print("\n[+] Testing Execution Cycle 3: Critical System Processing Thread Lock...")
    log_3 = monitor.audit_loop_step(actual_latency_ms=19.42)
    print(json.dumps(log_3, indent=2))
    
    # Compile the final cumulative compliance summary metrics
    compliance_rate = ((monitor.total_cycles - monitor.breach_count) / monitor.total_cycles) * 100
    print("\n" + "="*70)
    print(f"[#] COMPLIANCE METRICS PERFORMANCE REPORT:")
    print(f"[-] Total Monitored Cycles: {monitor.total_cycles}")
    print(f"[-] Documented Deadline Breaches: {monitor.breach_count}")
    print(f"[-] Net Pipeline Compliance Rate: {compliance_rate:.1f}%")
    print(f"[-] Accumulated System Timeline Drift: {monitor.accumulated_drift:.2f} ms")
    print("="*70)

if __name__ == "__main__":
    run_runtime_recovery_audit()