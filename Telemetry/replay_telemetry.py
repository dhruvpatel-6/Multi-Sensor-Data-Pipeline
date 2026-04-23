import json
import time

def replay_logs(file_path):
    print(f"--- [REPLAY] Starting Replay from {file_path} ---")
    try:
        with open(file_path, "r") as f:
            for line in f:
                data = json.loads(line)
                # Simulate the real-world timing (10Hz)
                time.sleep(0.1) 
                
                # Highlight critical moments in the replay
                status = data['health_status']
                prefix = ">>>" if status != "NOMINAL" else "   "
                
                print(f"{prefix} [{data['timestamp']}] State: {status} | Reason: {data['failure_reason']}")
                
    except FileNotFoundError:
        print("No log file found to replay.")

if __name__ == "__main__":
    replay_logs("logs/telemetry_data.jsonl")