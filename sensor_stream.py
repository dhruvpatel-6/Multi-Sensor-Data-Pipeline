import time
import json
import socket
import random
from datetime import datetime
import numpy as np

# ==============================================================================
# SPRINT MANDATE CONFIGURATION: REPRODUCIBILITY & MODE SWITCH
# ==============================================================================
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Modes: "LIVE" (Generates & saves logs) or "REPLAY" (Reads from recorded log)
MODE = "LIVE" 
RECORD_LOG_FILE = "quadruped_session_recording.jsonl"
# ==============================================================================

TERRAIN_PROFILES = {
    "TR-001_GRAVEL": {"traction": 0.72, "fail_prob": 0.05, "gait": "TROT", "energy": 45.2},
    "TR-002_MUD": {"traction": 0.34, "fail_prob": 0.28, "gait": "CRAWL_STABLE", "energy": 88.5},
    "TR-003_SAND": {"traction": 0.51, "fail_prob": 0.15, "gait": "AMBLE", "energy": 62.1},
    "TR-004_STAIRS": {"traction": 0.85, "fail_prob": 0.22, "gait": "STEP_PACE", "energy": 74.3}
}

def run_sensor_publisher(port=5555):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(1)
    
    print(f"📡 [HAL ENGINE] Mode: {MODE} | Seed: {RANDOM_SEED}")
    print(f"📡 Awaiting Analytics Core connection on port {port}...")
    conn, addr = server_socket.accept()
    print(f"📡 [HAL HANDSHAKE] Core linked successfully: {addr}")
    
    log_file = None
    if MODE == "LIVE":
        log_file = open(RECORD_LOG_FILE, "w", encoding="utf-8")
        print(f"💾 Recording session frames live to: {RECORD_LOG_FILE}")
    elif MODE == "REPLAY":
        print(f"🔄 Replaying session frames deterministically from: {RECORD_LOG_FILE}")
        try:
            with open(RECORD_LOG_FILE, "r", encoding="utf-8") as f:
                replay_frames = f.readlines()
        except FileNotFoundError:
            print(f"❌ Error: Cannot run REPLAY mode. File '{RECORD_LOG_FILE}' not found. Run in LIVE mode first.")
            server_socket.close()
            return

    step_counter = 0
    try:
        if MODE == "REPLAY":
            for line in replay_frames:
                if not line.strip(): continue
                # Replay identical frame packages down the socket pipeline
                conn.sendall((line.strip() + "\n").encode('utf-8'))
                time.sleep(0.15)
            print("🏁 [HAL REPLAY] Replay stream complete. All recorded frames piped.")
            
        else: # LIVE MODE
            while True:
                step_counter += 1
                start_time = time.perf_counter()
                
                terrain_keys = list(TERRAIN_PROFILES.keys())
                current_terrain = terrain_keys[(step_counter // 40) % len(terrain_keys)]
                t_data = TERRAIN_PROFILES[current_terrain]
                
                fault_mode = "NOMINAL"
                if step_counter % 50 in range(35, 40):
                    fault_mode = "IMU_DRIFT_CORRUPTION"
                elif step_counter % 50 in range(40, 45):
                    fault_mode = "ACTUATOR_THERMAL_SATURATION"
                elif step_counter % 50 in range(45, 50):
                    fault_mode = "CONTACT_SENSOR_FAULT"

                timestamp = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
                base_latency = float(np.random.uniform(2.8, 3.4))
                temperatures = [38.5, 39.2, 37.9, 40.1]
                torques = [12.4, 11.9, 13.1, 12.8]
                imu_reading = {"roll": round(random.uniform(-1.5, 1.5), 2), "pitch": round(random.uniform(-1.0, 1.0), 2)}
                contact_sensors = [1, 1, 1, 1] 
                
                if fault_mode == "IMU_DRIFT_CORRUPTION":
                    imu_reading["roll"] += float(random.uniform(15.5, 32.4))
                    base_latency = float(random.uniform(5.5, 8.2))
                elif fault_mode == "ACTUATOR_THERMAL_SATURATION":
                    temperatures = [t + float(random.uniform(45.5, 62.3)) for t in temperatures]
                    torques = [t * 0.4 for t in torques]
                elif fault_mode == "CONTACT_SENSOR_FAULT":
                    contact_sensors = [1, 0, -1, 1]

                execution_overhead = (time.perf_counter() - start_time) * 1000
                
                canonical_payload = {
                    "contract_version": "v3.0.0-Truth",
                    "frame_idx": step_counter,
                    "timestamp": timestamp,
                    "target_deadline_ms": 5.0,
                    "observed_latency_ms": round(base_latency + execution_overhead, 3),
                    "fault_injection_state": fault_mode,
                    "terrain_context": {
                        "terrain_id": current_terrain,
                        "traction_score": t_data["traction"],
                        "failure_probability": t_data["fail_prob"],
                        "recommended_gait": t_data["gait"],
                        "energy_cost_estimate": t_data["energy"]
                    },
                    "sensor_matrices": {
                        "temperatures_c": [round(t, 2) for t in temperatures],
                        "torques_nm": [round(t, 2) for t in torques],
                        "imu_orientation": imu_reading,
                        "contact_sensor_vector": contact_sensors
                    }
                }
                
                payload_str = json.dumps(canonical_payload)
                log_file.write(payload_str + "\n")
                log_file.flush()
                
                conn.sendall((payload_str + "\n").encode('utf-8'))
                time.sleep(0.15)
                
    except (ConnectionResetError, BrokenPipeError):
        print("🛑 [HAL ENGINE] Consumer disconnected abruptly.")
    finally:
        if log_file: log_file.close()
        server_socket.close()

if __name__ == "__main__":
    run_sensor_publisher()