# robot_control_interface.py
# Consolidated TANTRA Robotics Control and Mechanical Guardrail Interface Layer

import os
import sys

# Ensure workspace visibility for parent and sister modular packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class RobotControlInterface:
    def __init__(self):
        # ------------------------------------------------------------------
        # 1. PHYSICAL CONSTRAINTS (Units: Nm for Torque)
        # ------------------------------------------------------------------
        self.MAX_TORQUE = 12.0   # Maximum allowable safe hardware motor limit
        self.MIN_TORQUE = -12.0  # Minimum allowable safe hardware motor limit
        
        # ------------------------------------------------------------------
        # 2. JOINT LIMITS (Degrees)
        # ------------------------------------------------------------------
        self.JOINT_LIMITS = {
            "THIGH": (-45, 90), 
            "CALF": (-90, 0)
        }
        
        # Rigid topology map assignments for the 12-DOF Quadruped platform
        self.legs = ["FRONT_LEFT", "FRONT_RIGHT", "REAR_LEFT", "REAR_RIGHT"]
        self.joints = ["HIP", "THIGH", "CALF"]
        
        # Initialize internal unallocated state canvas vector
        self.commands = self._get_empty_map()

    def _get_empty_map(self):
        """
        Generates a clean, structural 12-DOF joint command canvas map 
        initialized completely to zero attributes.
        """
        return {leg: {joint: 0.0 for joint in self.joints} for leg in self.legs}

    def process_decisions(self, state, telemetry):
        """
        Evaluates higher-level health and failure states routed from the
        Failure Intelligence Engine (FID) and scales joint outputs accordingly.
        """
        # Determine base safety operational logic vectors
        if state in ["CRITICAL", "STOP"]:
            self._emergency_shutdown()
            self.commands["LED_STATUS"] = "RED"
            
        elif state == "CORRECTIVE_ACTION":
            self._calculate_balance(telemetry)
            self.commands["LED_STATUS"] = "YELLOW"
            
        else:
            self._apply_standard_gait()
            self.commands["LED_STATUS"] = "GREEN"

        # ------------------------------------------------------------------
        # 3. APPLY MECHANICAL CONSTRAINTS (The Physical Layer Protection)
        # ------------------------------------------------------------------
        self._enforce_physical_limits()
        
        return self.commands

    def _enforce_physical_limits(self):
        """
        The Mechanical Guardrail Layer. Implements rigid torque saturation clipping
        to ensure software outputs never breach safe physical hardware boundaries.
        """
        for leg in self.legs:
            for joint in self.joints:
                # Safeguard runtime execution loop against unexpected structural map omissions
                if joint not in self.commands[leg]:
                    continue
                    
                val = self.commands[leg][joint]
                
                # Constraint A: Torque Saturation Clipping
                # Prevents requesting unexecutable forces (e.g., commanding 100Nm when max capacity is 12Nm)
                clipped_val = max(self.MIN_TORQUE, min(self.MAX_TORQUE, val))
                
                # Format to a fixed precision profile for consistent network payload serialization
                self.commands[leg][joint] = round(clipped_val, 3)

    def _calculate_balance(self, telemetry):
        """
        Performs real-time proportional adjustment calculations on the front suspensions
        to actively counteract dangerous body pitch shifts.
        """
        # Extract live IMU tracking pitch variable with safe fallback
        pitch = telemetry.get('pitch', 0)
        
        # Proportional tracking adjustment calculation based on raw gyroscopic tilt
        adjustment = pitch * 0.08
        
        # Distribute compensating kinematic vector forces to the front drive components
        for leg in ["FRONT_LEFT", "FRONT_RIGHT"]:
            self.commands[leg]["THIGH"] += adjustment
            self.commands[leg]["CALF"] += (adjustment * 0.5)

    def _emergency_shutdown(self):
        """
        Instantaneous software safety trip. Disengages all actuator drive 
        forces by resetting the joint maps immediately to safe zero states.
        """
        self.commands = self._get_empty_map()
        self.commands["LED_STATUS"] = "RED"
        print("[PHYSICAL] TORQUE KILLED - ALL ACTUATORS DISENGAGED")

    def _apply_standard_gait(self):
        """
        Applies standard, steady-state baseline walking kinematic profiles 
        across all limbs during nominal operations.
        """
        for leg in self.legs:
            self.commands[leg]["THIGH"] = 0.5
            self.commands[leg]["CALF"] = 0.3


if __name__ == "__main__":
    # Local loop unit validation verification check
    print("Initializing standalone validation run for RobotControlInterface...")
    interface = RobotControlInterface()
    
    # Test Case A: Nominal evaluation check
    nominal_telemetry = {"pitch": 0.12, "roll": -0.05}
    nominal_result = interface.process_decisions("NOMINAL", nominal_telemetry)
    print(f"\n[TEST NOMINAL] System returned status indicators: {nominal_result['LED_STATUS']}")
    print(f" -> Front Left Kinematics Command Block: {nominal_result['FRONT_LEFT']}")
    
    # Test Case B: Active Tilt Correction Check
    tilted_telemetry = {"pitch": 15.4}
    corrective_result = interface.process_decisions("CORRECTIVE_ACTION", tilted_telemetry)
    print(f"\n[TEST CORRECTION] System returned status indicators: {corrective_result['LED_STATUS']}")
    print(f" -> Stabilized Front Left Command Block (Adjusted): {corrective_result['FRONT_LEFT']}")
    
    # Test Case C: Critical Emergency Trip Check
    critical_result = interface.process_decisions("STOP", tilted_telemetry)
    print(f"\n[TEST CRITICAL] System returned status indicators: {critical_result['LED_STATUS']}")
    print(f" -> Post-Shutdown Front Left Command Block: {critical_result['FRONT_LEFT']}")