# robot_control_interface.py - Phase 2: Control Translation Layer

class RobotControlInterface:
    def __init__(self):
        # 12-DOF Mapping: 4 Legs, 3 Joints each
        # Neutral Position (0.0 = Standing/Stable)
        self.commands = {
            "FRONT_LEFT":  {"HIP": 0.0, "THIGH": 0.0, "CALF": 0.0},
            "FRONT_RIGHT": {"HIP": 0.0, "THIGH": 0.0, "CALF": 0.0},
            "REAR_LEFT":   {"HIP": 0.0, "THIGH": 0.0, "CALF": 0.0},
            "REAR_RIGHT":  {"HIP": 0.0, "THIGH": 0.0, "CALF": 0.0},
            "LED_STATUS": "GREEN"
        }
        self.legs = ["FRONT_LEFT", "FRONT_RIGHT", "REAR_LEFT", "REAR_RIGHT"]
        self.joints = ["HIP", "THIGH", "CALF"]

    def process_decisions(self, fid_state, telemetry):
        """
        Translates FID states and Telemetry into specific joint torque values.
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
        Reflex logic for Quadruped Balance using per-joint mapping.
        If leaning forward (+pitch), increase Thigh and Calf torque to push up.
        """
        pitch = telemetry.get('pitch', 0)
        
        # P-Control Adjustment factor
        # Higher torque required for Thigh joints to lift body weight
        thigh_adj = pitch * 0.05
        calf_adj = pitch * 0.02

        if pitch > 0:
            # Adjusting Front Legs to counter forward pitch
            for leg in ["FRONT_LEFT", "FRONT_RIGHT"]:
                self.commands[leg]["THIGH"] += thigh_adj
                self.commands[leg]["CALF"] += calf_adj
            
            print(f"[CONTROL] Tilt detected ({pitch} deg). Adjusting Front Thighs by {thigh_adj:.2f}")

    def _emergency_shutdown(self):
        """Kills power to all 12 joints immediately."""
        for leg in self.legs:
            for joint in self.joints:
                self.commands[leg][joint] = 0.0
        
        print("[CONTROL] EMERGENCY SHUTDOWN ACTIVATED - ALL JOINTS SAFED")

    def _apply_standard_gait(self):
        """Placeholder for walking/standing logic across all legs."""
        for leg in self.legs:
            # Nominal standing torque to maintain posture
            self.commands[leg]["THIGH"] = 0.1 
            self.commands[leg]["CALF"] = 0.1