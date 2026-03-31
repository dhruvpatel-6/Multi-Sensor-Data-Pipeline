import random
import time
from datetime import datetime

def live_sensor_feed():
    """
    Phase 2 Simulator: Provides a continuous stream of IMU, 
    Depth, and CONTACT sensor data.
    """
    print("--- [SIMULATOR] Live Feed Started ---")
    while True:
        packet = {
            "timestamp": datetime.now().isoformat(),
            "sensors": {
                # 10% chance of 'None' to test your 'Last State' logic
                "imu": {
                    "accel_z": round(random.uniform(0.8, 1.2), 3)
                } if random.random() > 0.1 else None,
                
                "depth": {
                    "dist": round(random.uniform(0.1, 4.0), 2),
                    "contact": random.choice(["GROUNDED", "IN_AIR"]) # Added Contact Sensor
                }
            }
        }
        yield packet
        time.sleep(0.1) # 10Hz Frequency