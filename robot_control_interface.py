# robot_control_interface.py - Phase 2: Control Translation Layer

class RobotControlInterface:
    def __init__(self):
        # Default Neutral Position for all motors (0.0 = Standing)
        self.commands = {
            "FL_MOTOR": 0.0, "FR_MOTOR": 0.0,
            "RL_MOTOR": 0.0, "RR_MOTOR": 0.0,
            "LED_STATUS": "GREEN"
        }

    def process_decisions(self, fid_state, telemetry):
        """
        Translates FID states and Telemetry into motor values.
        """
        # Case 1: Critical Failure - Hard Stop
        if fid_state == "CRITICAL" or fid_state == "STOP":
            self._emergency_shutdown()
            self.commands["LED_STATUS"] = "RED"
        
        # Case 2: Unstable/Tilt - Corrective Action
        elif fid_state == "CORRECTIVE_ACTION":
            self._calculate_balance(telemetry)
            self.commands["LED_STATUS"] = "YELLOW"

        # Case 3: Nominal - Standard Walking
        else:
            self._apply_standard_gait()
            self.commands["LED_STATUS"] = "GREEN"
    
        return self.commands

    def _calculate_balance(self, telemetry):
        """
        Simplified 'Reflex' logic for Quadruped Balance.
        If Pitch is positive (leaning forward), increase front leg torque.
        """
        pitch = telemetry.get('pitch', 0)
        roll = telemetry.get('roll', 0)

        # Basic Proportional Control (P-Control)
        # If leaning forward (+ pitch), we "push" with front legs
        adjustment = pitch * 0.05 
        
        self.commands["FL_MOTOR"] += adjustment
        self.commands["FR_MOTOR"] += adjustment
        print(f"[CONTROL] Tilt detected ({pitch} deg). Adjusting Front Legs: {adjustment}")

    def _emergency_shutdown(self):
        for motor in ["FL_MOTOR", "FR_MOTOR", "RL_MOTOR", "RR_MOTOR"]:
            self.commands[motor] = 0.0  # Cut power
        self.commands["LED_STATUS"] = "RED"
        print("[CONTROL] EMERGENCY SHUTDOWN ACTIVATED")

    def _apply_standard_gait(self):
        # Placeholder for walking logic
        pass