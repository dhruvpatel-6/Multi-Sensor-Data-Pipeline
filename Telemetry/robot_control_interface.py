# Telemetry/robot_control_interface.py
# Phase 5: Robot Control Safety Interface

class RobotControlInterface:
    def __init__(self):
        pass

    def process_decisions(self, health_status, canonical_data):
        """
        Translates health status alerts into safe hardware actuation profiles.
        Ensures strict structural compatibility without exception crashes.
        """
        # Read incoming values safely
        joints = canonical_data.get("joint_states", {"hip": 0.0, "knee": 0.0})
        
        # Base nominal layout profile
        commands = {
            "FRONT_LEFT": {
                "HIP": float(joints.get("hip", 0.0)),
                "THIGH": float(joints.get("knee", 0.0))
            },
            "LED_STATUS": "GREEN_SOLID"
        }

        # Apply deterministic state-action safety constraints
        if health_status == "CRITICAL":
            commands["FRONT_LEFT"]["HIP"] = 0.0
            commands["FRONT_LEFT"]["THIGH"] = 0.0
            commands["LED_STATUS"] = "RED_FLASHING"
        elif health_status == "DEGRADED":
            commands["LED_STATUS"] = "AMBER_SLOW_BLINK"

        return commands