# Diagnostics/fault_intelligence.py
class QuadrupedFaultIntelligence:
    def __init__(self, maximum_latency_allowance_ms=15.0):
        self.max_latency = maximum_latency_allowance_ms

    def evaluate_system(self, json_contract_frame: dict) -> tuple:
        if not isinstance(json_contract_frame, dict):
            return "CRITICAL", "MALFORMED_CONTRACT_STREAM"

        current_health = json_contract_frame.get("health_status", "NOMINAL")
        current_reason = json_contract_frame.get("failure_reason", "NONE")
        recorded_latency = json_contract_frame.get("latency_ms", 0.0)

        if recorded_latency > self.max_latency:
            return "DEGRADED", "LATENCY_SPIKE_DETECTED"

        return current_health, current_reason
