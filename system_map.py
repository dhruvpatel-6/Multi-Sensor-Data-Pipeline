# robot_control_interface.py - Final Industrial Grade Control Layer

class RobotControlInterface:
    def __init__(self):
        # Physical Actuator Limits (Torque Saturation)
        self.MAX_TORQUE = 12.0  # Nm
        self.MIN_TORQUE = 0.0   # Current-limited minimum
        
        # PID Gains for Continuous Correction
        self.KP = 0.18 
        self.TARGET_PITCH = 0.0

        # Full 4-Leg / 12-DOF Model (Coordination Model)
        self.legs = ["FRONT_LEFT", "FRONT_RIGHT", "REAR_LEFT", "REAR_RIGHT"]
        self.joints = ["HIP", "THIGH", "CALF"]
        self.commands = {leg: {joint: 0.0 for joint in self.joints} for leg in self.legs}
        self.commands["LED_STATUS"] = "GREEN"

    def process_decisions(self, state, telemetry):
        """
        Gait-Level Behavior Controller
        Transitions between walking, standing, and stabilization phases.
        """
        # PHASE 1: RECOVERY / STABILIZATION (Closed-Loop)
        if state == "CORRECTIVE_ACTION":
            self._closed_loop_stabilization(telemetry)
            self.commands["LED_STATUS"] = "YELLOW"

        # PHASE 2: SAFETY (Critical Stop)
        elif state in ["CRITICAL", "STOP"]:
            self._emergency_shutdown()
            self.commands["LED_STATUS"] = "RED"

        # PHASE 3: NOMINAL (Stance/Gait)
        else:
            self._apply_standard_gait()
            self.commands["LED_STATUS"] = "GREEN"

        # FINAL WRAPPER: Actuator Saturation & Physical Limits
        self._enforce_actuator_limits()
        
        return self.commands

    def _closed_loop_stabilization(self, telemetry):
        """
        Sustained Correction & Per-Leg Coordination.
        Distributes load based on pitch error to stabilize the chassis.
        """
        pitch = telemetry.get('pitch', 0)
        error = pitch - self.TARGET_PITCH
        
        # Continuous Correction Calculation
        # Torque increases proportionally to the lean angle
        correction_torque = error * self.KP

        # Coordination: Sync Front legs for lift, Rear legs for bracing
        for leg in self.legs:
            if "FRONT" in leg:
                # Active lifting load
                self.commands[leg]["THIGH"] = correction_torque 
                self.commands[leg]["CALF"] = correction_torque * 0.5
            else:
                # Rear bracing load (Passive stabilization)
                self.commands[leg]["THIGH"] = 0.5 
                self.commands[leg]["CALF"] = 0.2

    def _apply_standard_gait(self):
        """Gait-level behavior: Neutral Stance."""
        for leg in self.legs:
            self.commands[leg]["THIGH"] = 0.2 # Holding torque
            self.commands[leg]["CALF"] = 0.1

    def _enforce_actuator_limits(self):
        """Actuator mapping to real mechanical constraints."""
        for leg in self.legs:
            for joint in self.joints:
                # Torque Saturation: Clipping values to real motor limits
                raw_val = self.commands[leg][joint]
                self.commands[leg][joint] = max(self.MIN_TORQUE, min(self.MAX_TORQUE, raw_val))

    def _emergency_shutdown(self):
        """Integration with load conditions: Total torque kill."""
        for leg in self.legs:
            for joint in self.joints:
                self.commands[leg][joint] = 0.0