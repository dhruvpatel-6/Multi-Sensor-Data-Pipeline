import socket
import json
import time
from analytics.anomaly_detector import PredictiveAnomalyDetector

def run_analytics_worker(input_port=5555, output_port=5556):
    detector = PredictiveAnomalyDetector(window_size=30, z_threshold=2.5)
    
    out_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    out_server.bind(('127.0.0.1', output_port))
    out_server.listen(1)
    
    print(f"⚙️ [ANALYTICS] Processing Core listening for dashboard hooks on port {output_port}...")
    
    in_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            in_client.connect(('127.0.0.1', input_port))
            print("⚙️ [ANALYTICS] Connected successfully to Edge Sensor Publisher stream.")
            break
        except socket.error:
            print("⏳ [ANALYTICS] Awaiting Edge stream source activation...")
            time.sleep(2)

    dash_conn, dash_addr = out_server.accept()
    print(f"⚙️ [ANALYTICS] Dashboard process registered from: {dash_addr}")

    buffer = ""
    try:
        while True:
            data = in_client.recv(4096).decode('utf-8')
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                
                frame = json.loads(line)
                is_anomaly, z_score = detector.observe_and_predict(frame["latency_ms"])
                
                frame["is_anomaly"] = is_anomaly
                frame["calculated_z"] = z_score
                frame["computed_status"] = "CRITICAL_BREACH" if is_anomaly else frame["mode"]
                
                if is_anomaly:
                    print(f"🛑 [ANOMALY] Frame #{frame['frame_idx']} marked anomalous! Z-score: {z_score}")
                else:
                    print(f"🟢 [PROCESSING] Frame #{frame['frame_idx']} verified. Latency: {frame['latency_ms']}ms")
                
                dash_conn.sendall((json.dumps(frame) + "\n").encode('utf-8'))
                
    except Exception as e:
        print(f"⚙️ [ANALYTICS] Worker runtime exception: {e}")
    finally:
        in_client.close()
        out_server.close()

if __name__ == "__main__":
    run_analytics_worker()