import time
from datetime import datetime # Added for Phase 5
from Drivers.pipeline_sim import live_sensor_feed
from Core.fid import FailureIntelligence

def start_continuous_pipeline():
    fid = FailureIntelligence()
    print("--- [MAIN] Phase 5: Structured Output Active ---")

    try:
        for raw_packet in live_sensor_feed():
            if not raw_packet or 'sensors' not in raw_packet:
                continue

            # Extraction
            sensors = raw_packet.get('sensors', {})
            imu_data = sensors.get('imu')
            imu_z = imu_data.get('accel_z') if imu_data else None
            
            depth_info = sensors.get('depth', {})
            dist = depth_info.get('dist')
            contact = depth_info.get('contact', 'UNKNOWN')

            # Run Intelligence (Phase 4 Logic)
            status, reason, var = fid.analyze_intelligence(imu_z, dist, contact)

            # --- PHASE 5: STRUCTURED STATE ---
            robot_state = {
                "timestamp": datetime.now().isoformat(),
                "imu": {"accel_z": imu_z, "variance": var},
                "depth": dist,
                "contact": contact,
                "health_status": status,
                "failure_reason": reason
            }

            # This print will now look like a JSON object in your terminal
            print(robot_state)

    except KeyboardInterrupt:
        print("\n--- Pipeline stopped ---")

if __name__ == "__main__":
    start_continuous_pipeline()
