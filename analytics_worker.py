import socket
import json
import time
import os
import numpy as np
from analytics.anomaly_detector import PredictiveAnomalyDetector

def run_analytics_worker(input_port=5555, output_port=5556):
    detector = PredictiveAnomalyDetector(window_size=30, z_threshold=2.2)
    
    out_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    out_server.bind(('127.0.0.1', output_port))
    out_server.listen(1)
    
    print(f"⚙️ [ANALYTICS ENGINE] Listening for dashboard pipelines on port {output_port}...")
    
    in_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            in_client.connect(('127.0.0.1', input_port))
            print("⚙️ [ANALYTICS ENGINE] Successfully matched with HAL socket stream.")
            break
        except socket.error:
            print("⏳ [ANALYTICS ENGINE] Polling for active HAL server instance...")
            time.sleep(2)

    dash_conn, dash_addr = out_server.accept()
    
    # Execution metrics cache for honest deadline tracking
    latency_history = []
    deadline_violations = 0
    terrain_intelligence_agg = {}

    buffer = ""
    try:
        while True:
            data = in_client.recv(4096).decode('utf-8')
            if not data: break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip(): continue
                
                frame = json.loads(line)
                
                # Extract parameters for evaluation
                latency = frame["observed_latency_ms"]
                deadline = frame["target_deadline_ms"]
                fault_state = frame["fault_injection_state"]
                terrain = frame["terrain_context"]["terrain_id"]
                
                latency_history.append(latency)
                if latency > deadline:
                    deadline_violations += 1
                
                # Dynamic Z-Score evaluation
                is_anomaly, z_score = detector.observe_and_predict(latency)
                
                # Calculate real-time performance bounds
                compliance_rate = round(((len(latency_history) - deadline_violations) / len(latency_history)) * 100, 2)
                
                # --- TELEMETRY SIGNATURE MAPPING & PROPAGATION LOGIC ---
                stability_score = 100.0
                slip_signature = "NOMINAL_TRACKING"
                control_response = "MAINTAIN_GAIT_VELOCITY"
                
                if fault_state == "IMU_DRIFT_CORRUPTION":
                    stability_score -= 45.5
                    slip_signature = "HIGH_LATERAL_DRIFT_DETECTION"
                    control_response = "ENGAGE_IMU_RESET_INTEGRATOR"
                elif fault_state == "ACTUATOR_THERMAL_SATURATION":
                    stability_score -= 30.0
                    slip_signature = "TORQUE_LIMIT_ATTENUATION"
                    control_response = "REDUCE_GAIT_DUTY_CYCLE"
                elif -1 in frame["sensor_matrices"]["contact_sensor_vector"]:
                    stability_score -= 60.0
                    slip_signature = "CONTACT_SENSOR_DISCONNECT"
                    control_response = "FALLBACK_KINEMATIC_ESTIMATION"
                
                # Apply terrain reduction modifiers
                stability_score -= (1.0 - frame["terrain_context"]["traction_score"]) * 20
                stability_score = max(5.0, round(stability_score, 2))
                
                # Enrich payloads mapping data fields across boundaries
                frame["analytics"] = {
                    "is_anomaly": is_anomaly,
                    "calculated_z": z_score,
                    "stability_score": stability_score,
                    "slip_signature": slip_signature,
                    "control_response": control_response,
                    "compliance_metrics": {
                        "cumulative_compliance_pct": compliance_rate,
                        "total_violations": deadline_violations,
                        "running_mean_jitter_ms": round(float(np.std(latency_history[-20:])) if len(latency_history) > 1 else 0.0, 3)
                    }
                }
                
                # --- ASYNC EXPORT: TERRAIN INTELLIGENCE DATASET GENERATION ---
                terrain_intelligence_agg[terrain] = {
                    "terrain_id": terrain,
                    "traction_score": frame["terrain_context"]["traction_score"],
                    "failure_probability": frame["terrain_context"]["failure_probability"],
                    "slip_signature": slip_signature,
                    "control_response": control_response,
                    "recommended_gait": frame["terrain_context"]["recommended_gait"],
                    "energy_cost_estimate": frame["terrain_context"]["energy_cost_estimate"],
                    "thermal_impact_c": round(max(frame["sensor_matrices"]["temperatures_c"]), 2),
                    "recovery_success_rate_pct": round(stability_score * 0.95, 2)
                }
                
                if frame["frame_idx"] % 10 == 0:
                    with open("terrain_profile.json", "w") as json_file:
                        json.dump(terrain_intelligence_agg, json_file, indent=4)

                # Output to processing terminal
                print(f"📦 Frame #{frame['frame_idx']} processed [Terrain: {terrain}] | Status: {fault_state} | Compliance: {compliance_rate}%")
                
                dash_conn.sendall((json.dumps(frame) + "\n").encode('utf-8'))
                
    except Exception as e:
        print(f"⚙️ [ANALYTICS ENGINE] Exception encountered: {e}")
    finally:
        in_client.close()
        out_server.close()

if __name__ == "__main__":
    run_analytics_worker()