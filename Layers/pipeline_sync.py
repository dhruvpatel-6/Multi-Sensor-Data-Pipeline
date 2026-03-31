import json
import os

def sync_robot_data(input_file="raw_sensor_logs.json"):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found! Run sensor_sim.py first.")
        return

    with open(input_file, "r") as f:
        raw_data = json.load(f)

    # Separate the messy data into two buckets
    imu_data = [p for p in raw_data if p["sensor"] == "IMU"]
    depth_data = [p for p in raw_data if p["sensor"] == "DEPTH"]
    
    synced_output = []

    print(f"Syncing {len(depth_data)} Depth readings with closest IMU data...")

    # We loop through Depth (the slower sensor) and find the best IMU match
    for d_packet in depth_data:
        d_time = d_packet["timestamp"]
        
        # Find the IMU entry that happened closest to this Depth entry
        closest_imu = min(imu_data, key=lambda x: abs(x["timestamp"] - d_time))
        
        # Create a single "Robot State" packet
        combined = {
            "timestamp": d_time,
            "imu_accel_z": closest_imu["data"]["accel_z"],
            "depth_distance": d_packet["data"]["distance"],
            "sync_error_ms": round(abs(closest_imu["timestamp"] - d_time) * 1000, 2)
        }
        synced_output.append(combined)

    # Save Deliverable: Processed Data
    output_file = "processed_synced_logs.json"
    with open(output_file, "w") as f:
        json.dump(synced_output, f, indent=4)
    
    print(f"--- SUCCESS ---")
    print(f"Created {output_file} with {len(synced_output)} synced states.")

if __name__ == "__main__":
    sync_robot_data()