import random

class SimulatedRobot:
    def __init__(self):
        self.current_mode = "NOMINAL"

    def set_simulation_mode(self, mode: str):
        """Phase 5 Fault Injector Hook - used to simulate upstream failures."""
        self.current_mode = mode

    def get_full_hardware_stack(self):
        """
        Simulates Rugved's Actuator Control System boundary output.
        Provides unflattened 12-DOF joint states, torques, and raw IMU feeds.
        """
        # Default normal physics readings
        pitch_val = 0.5 + random.uniform(-0.05, 0.05)
        status_flag = "NOMINAL"
        reason_flag = "NONE"
        
        # Structure joint states strictly tracking HIP and KNEE per the specification contract
        joint_states = {
            "FRONT_LEFT":  {"HIP": 0.12, "KNEE": -0.34},
            "FRONT_RIGHT": {"HIP": 0.12, "KNEE": -0.34},
            "REAR_LEFT":   {"HIP": -0.05, "KNEE": 0.18},
            "REAR_RIGHT":  {"HIP": -0.05, "KNEE": 0.18}
        }
        
        torque_outputs = {
            "FRONT_LEFT": 1.25,
            "FRONT_RIGHT": 1.25,
            "REAR_LEFT": 0.85,
            "REAR_RIGHT": 0.85
        }

        # Fault Injection Triggers (for Phase 5 safety verification boundaries)
        if self.current_mode == "MISSING_ACTUATOR":
            # Simulate critical data dropping from communication line
            joint_states = {}
            torque_outputs = {}
            status_flag = "DEGRADED"
            reason_flag = "ACTUATOR_COMM_DROP"
            
        elif self.current_mode == "GHOST_DIVE":
            # Simulate corrupt sensor packet boundary fault
            pitch_val = -99.0  
            status_flag = "CRITICAL"
            reason_flag = "IMU_SENSOR_CORRUPTION"

        return {
            "joint_states": joint_states,
            "torque_outputs": torque_outputs,
            "imu": {
                "pitch": pitch_val,
                "roll": 0.08,
                "accel_z": 9.81
            },
            "contact": [True, True, True, True],
            "status": status_flag,
            "reason": reason_flag
        }