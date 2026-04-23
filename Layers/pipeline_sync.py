import time

# Phase 1 & 2: Interface Definition & Control-Loop Constants
UPDATE_RATE_HZ = 10  # Required >= 10Hz for stability
LATENCY_MAX_MS = 100 

def format_robot_state(imu, depth, contact, health, reason):
    """
    Standardized Output Schema.
    Ensures the 'Robot Brain' receives a predictable data contract.
    """
    return {
        "timestamp": time.time(),
        "orientation_accel": imu,
        "terrain_distance": depth,
        "contact_state": contact,
        "health_status": health,
        "failure_reason": reason
    }
class DataSynchronizer:
    def __init__(self):
        self.last_state = None

    def bundle(self, raw_data):
        # Your logic to sync IMU, Depth, etc.
        # Return a single dictionary (the packet)
        return raw_data