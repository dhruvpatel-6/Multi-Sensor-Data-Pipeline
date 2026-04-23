# Drivers/pipeline_sim.py - Updated for Task 4 Control Integration
import random
import time
from datetime import datetime

class SimulatedRobot:
    def __init__(self):
        self.mode = "NOMINAL"

    def set_simulation_mode(self, mode):
        """Allows the test script to trigger failures"""
        self.mode = mode
        print(f"\n[SIMULATOR] Mode changed to: {self.mode}")

    def get_telemetry(self):
        """Provides a 10Hz stream of data based on the current mode"""
        # Base stable values
        pitch = random.uniform(-1.0, 1.0)
        roll = random.uniform(-1.0, 1.0)
        status = "HEALTHY"

        # Inject Failure Scenarios
        if self.mode == "STIMULATE_TILT":
            pitch = random.uniform(20.0, 30.0) # Trigger CORRECTIVE_ACTION
            
        elif self.mode == "GHOST_DIVE":
            status = "GHOST_DIVE" # Trigger EMERGENCY_STOP
            
        elif self.mode == "SENSOR_LAG":
            time.sleep(0.15) # Force latency > 100ms to trigger SAFE_MODE

        packet = {
            "timestamp": datetime.now().isoformat(),
            "pitch": round(pitch, 2),
            "roll": round(roll, 2),
            "status": status,
            "depth": {
                "dist": round(random.uniform(0.1, 4.0), 2),
                "contact": random.choice(["GROUNDED", "IN_AIR"])
            }
        }
        return packet

# Keeping your generator for backward compatibility if needed
def live_sensor_feed():
    sim = SimulatedRobot()
    while True:
        yield sim.get_telemetry()
        time.sleep(0.1)
        
def get_telemetry(self):
    # Standard healthy values
    pitch, roll, status = 0.5, 0.2, "HEALTHY"

    # Hook for Phase 5: Force a tilt
    if self.mode == "STIMULATE_TILT":
        pitch = 25.5  # This should trigger CORRECTIVE_ACTION in FID
        
    # Hook for Phase 6: Force a crash
    elif self.mode == "GHOST_DIVE":
        status = "GHOST_DIVE" # This should trigger STOP in FID

    return {"pitch": pitch, "roll": roll, "status": status}