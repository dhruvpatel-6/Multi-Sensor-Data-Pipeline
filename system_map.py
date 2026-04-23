# system_map.py - Phase 1: Virtual System Mapping

class QuadrupedMapping:
    def __init__(self):
        # 1. INPUTS: What data do we expect?
        self.inputs = {
            "imu": ["pitch", "roll", "yaw"],
            "leg_feedback": ["fl_pos", "fr_pos", "rl_pos", "rr_pos"]
        }

        # 2. DECISION STATES: How does FID interpret inputs?
        self.decision_logic = {
            "STABLE": "Continue Gait",
            "TILT_DETECTED": "Trigger Corrective Action",
            "SENSOR_LOSS": "Enter Safe Mode",
            "CRITICAL_FAILURE": "Emergency Stop"
        }

        # 3. OUTPUTS: Virtual Actuator Signals
        # we define the "Command Structure"
        #Neutral Standing Position. During a CORRECTIVE_ACTION,code will change these values like 1.5 or -0.8 to move the legs.
        self.actuator_commands = {
            "FL_MOTOR": 0.0, # Target Position/Velocity
            "FR_MOTOR": 0.0,
            "RL_MOTOR": 0.0,
            "RR_MOTOR": 0.0,
            "LED_STATUS": "GREEN"
        }
        #GREEN: System is Nominal.
        #YELLOW: FID has detected a minor anomaly (Safe Mode).
        #RED: Critical failure (Emergency Stop).

    def get_system_summary(self):
        print("--- PHASE 1: SYSTEM MAP INITIALIZED ---")
        print(f"Tracking {len(self.inputs)} Sensor Categories")
        print(f"Mapping to {len(self.actuator_commands)} Virtual Actuators")
        print("Status: Ready for Control Interface Integration.")

if __name__ == "__main__":
    mapper = QuadrupedMapping()
    mapper.get_system_summary()