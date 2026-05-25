# Hardware/quadruped_hardware_bridge.py
class QuadrupedHardwareBridge:
    def __init__(self):
        self.mode = "NOMINAL"

    def set_simulation_mode(self, mode: str):
        self.mode = mode

    def get_full_hardware_stack(self) -> dict:
        if self.mode == "FAULT_MISSING_DATA":
            return {"joint_states": None, "imu_data": {}, "torque_outputs": {}, "contact_state": [0, 0, 0, 0]}
        
        if self.mode == "FAULT_CORRUPT_SENSOR":
            return {
                "joint_states": {
                    "FL": {"abduction": 0.0, "hip": 0.1, "knee": -0.2},
                    "FR": {"abduction": 0.0, "hip": 0.1, "knee": -0.2},
                    "RL": {"abduction": 0.0, "hip": 0.1, "knee": -0.2},
                    "RR": {"abduction": 0.0, "hip": 0.1, "knee": -0.2}
                },
                "imu_data": {"pitch": -99.0, "roll": 0.0, "accel_z": 0.0},
                "torque_outputs": {},
                "contact_state": [1, 1, 1, 1]
            }

        return {
            "joint_states": {
                "FL": {"abduction": 0.0, "hip": 0.4, "knee": -0.8},
                "FR": {"abduction": 0.0, "hip": 0.4, "knee": -0.8},
                "RL": {"abduction": 0.0, "hip": -0.2, "knee": 0.5},
                "RR": {"abduction": 0.0, "hip": -0.2, "knee": 0.5}
            },
            "imu_data": {"pitch": 1.2, "roll": -0.4, "accel_z": 9.79},
            "contact_state": [1, 1, 1, 1],
            "torque_outputs": {
                "FL": {"abduction": 0.5, "hip": 12.4, "knee": -18.2},
                "FR": {"abduction": -0.5, "hip": 12.1, "knee": -17.9},
                "RL": {"abduction": 0.1, "hip": -4.2, "knee": 6.8},
                "RR": {"abduction": -0.1, "hip": -4.0, "knee": 6.5}
            }
        }
