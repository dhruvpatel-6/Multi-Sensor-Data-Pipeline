import time
import random
from analytics.anomaly_detector import PredictiveAnomalyDetector

def run_simulation_test():
    print("====================================================")
    print("[+] INITIALIZING EDGE COMPUTATION ANALYTICS MODULE")
    print("====================================================")
    
    # Initialize detector instance with default window parameters
    detector = PredictiveAnomalyDetector(window_size=30, z_threshold=2.5)
    
    print("[*] Priming baseline history buffers with nominal states...")
    
    # Simulating 45 cycles of live control loop telemetry streaming
    for tick in range(1, 46):
        if tick <= 35:
            # 1. Normal State: Stable control latency floating around 3.8ms
            current_latency = random.uniform(3.6, 4.0)
        elif tick <= 40:
            # 2. Timing Jitter Incident: Simulating micro-spikes (Minor Anomalies)
            current_latency = random.uniform(5.5, 7.2)
        else:
            # 3. Critical Structural Fault: Thermal or scheduling runaway breach!
            current_latency = random.uniform(18.5, 24.0)
            
        # Pass data into your observation algorithm
        is_anomaly, z_score = detector.observe_and_predict(current_latency)
        
        # Format display terminal strings based on real-time classification flags
        timestamp = f"Tick #{tick:02d}"
        metrics_log = f"Latency: {current_latency:.2f} ms | Calculated Z-Score: {z_score:.2f}"
        
        if is_anomaly:
            print(f"🛑 [BREACH] {timestamp} -> {metrics_log} (ANOMALY DETECTED!)")
        else:
            if tick > 10:
                print(f"🟢 [NOMINAL] {timestamp} -> {metrics_log}")
            else:
                print(f"⚪ [WARNING] {timestamp} -> Latency: {current_latency:.2f} ms (Buffering data...)")
                
        time.sleep(0.05) # Emulate fast execution ticks

if __name__ == "__main__":
    run_simulation_test()