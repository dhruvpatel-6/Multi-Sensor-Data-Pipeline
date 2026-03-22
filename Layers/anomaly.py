import json

def run_diagnostics(input_file="processed_synced_logs.json"):
    with open(input_file, "r") as f:
        data = json.load(f)

    clean_data = []
    anomaly_count = 0

    print("--- STARTING DATA DIAGNOSTICS ---")

    for entry in data:
        # 1. Check for Depth Spikes (The 99.9 error)
        if entry["depth_distance"] > 10.0:
            entry["health_status"] = "CRITICAL: SENSOR_SPIKE"
            anomaly_count += 1
        
        # 2. Check for High Latency (Sync Error > 50ms)
        elif entry["sync_error_ms"] > 50:
            entry["health_status"] = "WARNING: HIGH_LATENCY"
            anomaly_count += 1
            
        else:
            entry["health_status"] = "HEALTHY"
        
        clean_data.append(entry)

    # Save the final flagged data
    with open("final_flagged_logs.json", "w") as f:
        json.dump(clean_data, f, indent=4)

    print(f"Diagnostics Complete. Found {anomaly_count} issues.")
    print("Saved to: final_flagged_logs.json")

if __name__ == "__main__":
    run_diagnostics()