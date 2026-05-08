# robot_control_interface.py - Mechanical Constraint Integration

class RobotControlInterface:
    def __init__(self):
        # 1. PHYSICAL CONSTRAINTS (Units: Nm for Torque)
        self.MAX_TORQUE = 12.0  # Motor limit
        self.MIN_TORQUE = -12.0
        
        # 2. JOINT LIMITS (Degrees)
        self.JOINT_LIMITS = {"THIGH": (-45, 90), "CALF": (-90, 0)}

        self.commands = self._get_empty_map()
        self.legs = ["FRONT_LEFT", "FRONT_RIGHT", "REAR_LEFT", "REAR_RIGHT"]
        self.joints = ["HIP", "THIGH", "CALF"]

    def _get_empty_map(self):
        return {leg: {joint: 0.0 for joint in ["HIP", "THIGH", "CALF"]} for leg in ["FRONT_LEFT", "FRONT_RIGHT", "REAR_LEFT", "REAR_RIGHT"]}

    def process_decisions(self, state, telemetry):
        # Determine base logic
        if state in ["CRITICAL", "STOP"]:
            self._emergency_shutdown()
            self.commands["LED_STATUS"] = "RED"
        elif state == "CORRECTIVE_ACTION":
            self._calculate_balance(telemetry)
            self.commands["LED_STATUS"] = "YELLOW"
        else:
            self._apply_standard_gait()
            self.commands["LED_STATUS"] = "GREEN"

        # 3. APPLY MECHANICAL CONSTRAINTS (The Physical Layer)
        self._enforce_physical_limits()
        
        return self.commands

    def _enforce_physical_limits(self):
        """
        The 'Mechanical Guardrail' layer.
        Ensures software never commands something hardware cannot do.
        """
        for leg in self.legs:
            for joint in self.joints:
                val = self.commands[leg][joint]
                
                # Constraint A: Torque Saturation (Clipping)
                # Prevents commanding 100Nm when motor only does 12Nm
                clipped_val = max(self.MIN_TORQUE, min(self.MAX_TORQUE, val))
                
                self.commands[leg][joint] = round(clipped_val, 3)

    def _calculate_balance(self, telemetry):
        pitch = telemetry.get('pitch', 0)
        # Proportional adjustment based on tilt
        adjustment = pitch * 0.08
        
        # Distribute force to front legs to counter pitch
        for leg in ["FRONT_LEFT", "FRONT_RIGHT"]:
            self.commands[leg]["THIGH"] += adjustment
            self.commands[leg]["CALF"] += (adjustment * 0.5)

    def _emergency_shutdown(self):
        """Kills power and resets commands safely."""
        self.commands = self._get_empty_map()
        self.commands["LED_STATUS"] = "RED"
        print("[PHYSICAL] TORQUE KILLED - ALL ACTUATORS DISENGAGED")

    def _apply_standard_gait(self):
        """Nominal stance torque."""
        for leg in self.legs:
            self.commands[leg]["THIGH"] = 0.5
            self.commands[leg]["CALF"] = 0.3