import json

def detect_anomalies(input_file="processed_synced_logs.json"):
    with open(input_file, "r") as f:
        data = json.load(f)

    anomalies = []
    print("Scanning for sensor failures...")

    for entry in data:
        # 1. Detect Depth Spikes
        if entry["depth_distance"] > 10.0:
            entry["status"] = "ANOMALY: SENSOR_SPIKE"
            anomalies.append(entry)

        # 2. Detect High Latency (Sync Error)
        elif entry["sync_error_ms"] > 50:
            entry["status"] = "ANOMALY: HIGH_LATENCY"
            anomalies.append(entry)
        
        else:
            entry["status"] = "HEALTHY"

    # Save the Final Processed Data
    with open("final_flagged_logs.json", "w") as f:
        json.dump(data, f, indent=4)

    print(f"Detected {len(anomalies)} anomalies in the pipeline.")

if __name__ == "__main__":
    detect_anomalies()