import time
import json
import socket
import random
from datetime import datetime
import numpy as np

def run_sensor_publisher(port=5555):
    # Establish local IPC Socket server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(1)
    
    print(f"📡 [EDGE] Sensor Publisher stream initiated on port {port}. Awaiting Analytics connection...")
    
    conn, addr = server_socket.accept()
    print(f"📡 [EDGE] Analytics handshaking established with: {addr}")
    
    step_counter = 0
    modes = ["NOMINAL", "TIMING_JITTER", "PARTIAL_ACTUATOR_DEGRADATION", "CRITICAL_FAULTS"]
    
    try:
        while True:
            step_counter += 1
            # Periodically shift phase states to emulate structural changes
            if step_counter % 60 <= 40:
                current_mode = "NOMINAL"
            elif step_counter % 60 <= 48:
                current_mode = "TIMING_JITTER"
            else:
                current_mode = random.choice(modes)

            timestamp = datetime.utcnow().strftime("%H:%M:%S.%f")[:-3]
            latency = float(np.random.uniform(3.6, 4.0))
            bus_status = "HEALTHY"
            base_torques = [12.5, 14.0, 11.8, 13.5]
            base_temps = [38.2, 39.1, 37.9, 40.4]
            
            if current_mode == "NOMINAL":
                temps = [t + random.uniform(-0.2, 0.2) for t in base_temps]
                torques = base_torques
            elif current_mode == "TIMING_JITTER":
                latency = float(random.uniform(6.5, 14.2))
                temps = base_temps
                torques = base_torques
            elif current_mode == "PARTIAL_ACTUATOR_DEGRADATION":
                temps = [t + 12.4 for t in base_temps]
                torques = [min(14.5, t) for t in base_torques]
                bus_status = "CURRENT_LIMITED"
            elif current_mode == "CRITICAL_FAULTS":
                latency = float(random.uniform(18.0, 25.5))
                temps = [94.2, 98.6, 95.1, 102.4]
                torques = [0.0, 0.0, 0.0, 0.0]
                bus_status = "TIMEOUT_CRITICAL"

            payload = {
                "frame_idx": step_counter,
                "timestamp": timestamp,
                "mode": current_mode,
                "latency_ms": round(latency, 2),
                "bus_status": bus_status,
                "temperatures": [round(t, 1) for t in temps],
                "torques": [round(t, 2) for t in torques]
            }
            
            # Stream packetized string over local IPC channel
            conn.sendall((json.dumps(payload) + "\n").encode('utf-8'))
            time.sleep(0.15) # High frequency tick speed
            
    except (ConnectionResetError, BrokenPipeError):
        print("🛑 [EDGE] Pipeline downstream link disconnected.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    run_sensor_publisher()