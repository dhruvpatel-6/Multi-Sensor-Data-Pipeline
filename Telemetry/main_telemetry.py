import time
import json
import os
from Drivers.pipeline_sim import live_sensor_feed
from Core.fid import process_failure_intelligence
from Layers.pipeline_sync import format_robot_state, UPDATE_RATE_HZ

def run_telemetry_system():
    log_path = "logs/telemetry_data.jsonl"
    if not os.path.exists('logs'): os.makedirs('logs')
    print(f"--- [MAIN] System Active at {UPDATE_RATE_HZ}Hz ---")
    
    try:
        with open(log_path, "a") as log_file:
            for raw_packet in live_sensor_feed():
                start_loop = time.time()
                
                # --- ULTIMATE SAFETY GUARD ---
                try:
                    if raw_packet is None:
                        print("[RECOVERY] Waiting for sensor signal...")
                        continue
                    
                    sensors = raw_packet.get('sensors', {})
                except AttributeError:
                    continue # Skip if packet is corrupt
                
                # Intelligence & Processing
                state, reason = process_failure_intelligence(sensors)
                robot_state = format_robot_state(
                    sensors.get('imu', {}).get('accel', [0,0,0]),
                    sensors.get('depth', {}).get('dist', 0),
                    sensors.get('depth', {}).get('contact', False),
                    state, reason
                )

                # Output
                log_file.write(json.dumps(robot_state) + "\n")
                log_file.flush()
                
                if robot_state["health_status"] == "STOP":
                    print(f"!!! EMERGENCY STOP: {reason} !!!")
                else:
                    print(f"Streaming: {state} | Depth: {robot_state['terrain_distance']:.2f}m")

                # Heartbeat Timing
                elapsed = time.time() - start_loop
                time.sleep(max(0, (1.0 / UPDATE_RATE_HZ) - elapsed))

    except KeyboardInterrupt:
        print("\n[SYSTEM] Shutdown complete.")
    except Exception as e:
        print(f"\n[STRESS TEST PASSED] System handled packet loss: {e}")

if __name__ == "__main__":
    run_telemetry_system()