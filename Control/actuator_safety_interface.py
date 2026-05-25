# Control/actuator_safety_interface.py
class ActuatorSafetyInterface:
    def process_safety_action(self, health_status: str, failure_reason: str) -> str:
        if health_status == "CRITICAL":
            return "RED_FLASHING_HAZARD_ENGAGED_SAFETY_BRAKE_ACTIVE"
        if health_status == "DEGRADED":
            return f"AMBER_SLOW_BLINK_WARNING_STATE_{failure_reason}"
        return "GREEN_STEADY_SYSTEM_NOMINAL"
