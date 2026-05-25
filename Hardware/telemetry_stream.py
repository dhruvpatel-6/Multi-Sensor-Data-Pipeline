import time
import random
from datetime import datetime

# PHASE 1 & 5: SETTING THE FREQUENCY (10Hz = 0.1s)
IMU_INTERVAL = 0.1 
DEPTH_INTERVAL = 0.5 

def get_live_imu():
    """Simulates Usman's sensor interface providing live IMU data"""
    # Adding Phase 4: Robustness (Simulating a 5% chance of a missing packet)
    if random.random() < 0.05:
        return None
    return {
        "accel_x": round(random.uniform(-1, 1), 2),
        "timestamp": datetime.now().isoformat()
    }

def get_live_depth():
    """Simulates live depth data"""
    return {"distance": round(random.uniform(0.5, 3.0), 2)}

def stream_pipeline():
    print("--- Starting Real-Time Telemetry Stream ---")
    
    # PHASE 2: LAST STATE LOGIC (For synchronization)
    last_contact_state = "TOUCHING" 
    
    try:
        while True:
            # 1. Capture Data
            imu_data = get_live_imu()
            depth_data = get_live_depth()
            
            # PHASE 4: DATA INTEGRITY (Handling missing packets)
            if imu_data is None:
                print("WARNING: IMU Packet Dropped. Maintaining System Safety...")
                health = "DEGRADED"
                reason = "IMU_DATA_MISSING"
            else:
                # PHASE 3: FAILURE INTELLIGENCE (Simple Correlation)
                # If distance is very low but accel is high, it's a collision risk
                if depth_data['distance'] < 0.8 and abs(imu_data['accel_x']) > 0.8:
                    health = "CRITICAL"
                    reason = "COLLISION_IMMINENT"
                else:
                    health = "HEALTHY"
                    reason = "NOMINAL"

            # PHASE 5: STRUCTURED ROBOT STATE (The mandatory dictionary)
            robot_state = {
                "timestamp": datetime.now().isoformat(),
                "imu": imu_data,
                "depth": depth_data,
                "contact": last_contact_state, # Integrated from Phase 2
                "health_status": health,       # Corrected naming bug
                "failure_reason": reason
            }

            print(f"[{robot_state['health_status']}] Data: {robot_state}")
            
            # Wait for the next 'heartbeat' (10Hz)
            time.sleep(IMU_INTERVAL)

    except KeyboardInterrupt:
        print("\nStream stopped by user.")

if __name__ == "__main__":
    stream_pipeline()