import time
import json
import random
import os

def generate_sensor_data(duration_seconds=5):
    start_time = time.time()
    raw_logs = []
    
    # Settings
    imu_hz = 0.01    # 100Hz
    depth_hz = 0.1   # 10Hz
    
    last_imu_time = 0
    last_depth_time = 0
    
    print("--- SIMULATION STARTED (WITH NOISE) ---")
    
    current_time = 0
    while current_time < duration_seconds:
        current_time = time.time() - start_time
        
        # 1. IMU with DRIFT
        if (current_time - last_imu_time) >= imu_hz:
            drift = current_time * 0.05 # Error grows over time
            accel_z = 9.8 + random.uniform(-0.1, 0.1) + drift
            
            imu_packet = {
                "timestamp": round(current_time, 4),
                "sensor": "IMU",
                "data": {"accel_z": round(accel_z, 3)}
            }
            raw_logs.append(imu_packet)
            last_imu_time = current_time

        # 2. DEPTH with SPIKES
        if (current_time - last_depth_time) >= depth_hz:
            distance = random.uniform(0.5, 2.0)
            # 5% chance of a "bad" reading (Spike)
            if random.random() > 0.95:
                distance = 99.9 
            
            depth_packet = {
                "timestamp": round(current_time, 4),
                "sensor": "DEPTH",
                "data": {"distance": round(distance, 2)}
            }
            raw_logs.append(depth_packet)
            last_depth_time = current_time

        # 3. CONTACT SENSOR (Random Events)
        if random.random() > 0.995: # Occasional foot touch
            contact_packet = {
                "timestamp": round(current_time, 4),
                "sensor": "CONTACT",
                "data": {"touch": 1}
            }
            raw_logs.append(contact_packet)
            
        time.sleep(0.001)

    # SAVE
    with open("raw_sensor_logs.json", "w") as f:
        json.dump(raw_logs, f, indent=4)
    
    print(f"--- FINISHED --- Saved {len(raw_logs)} noisy packets.")

if __name__ == "__main__":
    generate_sensor_data()