🤖 Multi-Sensor Robotic Data Pipeline 
|
Dhruv Patel | Robotics Systems – Test 1

📌 Project Purpose :

This project defines a high-reliability system architecture for a multi-sensor data pipeline. It integrates an IMU, Distance sensor, and Contact sensors into a single, failure-aware, and time-synchronized prototype. The design is "integration-ready," meaning it is structured to plug directly into a real robotic platform in the future.

🏗️ System Architecture & Sensor Stack :

The architecture is built on a 10 Hz timing reference to ensure all data is perfectly aligned.

• Primary Timing (IMU): Operating at 10 Hz, the Inertial Measurement Unit provides Acceleration and Orientation $[roll, pitch, yaw]$. It is the most critical sensor in the pipeline.

• Terrain Awareness (Distance): This sensor provides range data in meters (Valid: 0.05m to 4.0m) at a 2 Hz frequency.

🔄 The 4-Step Data Flow :

The system processes data through a logical sequence to ensure "Clarity of Architecture":

1. Ingestion: The system reads raw, unsynchronized CSV files from the IMU and Distance sensors.

2. Synchronization: Using a Timestamp Handshake, the pipeline finds the "Closest Neighbor" in the 2 Hz data for every 10 Hz IMU reading to create a unified packet.

3.  Validation: A Threshold Rule is applied (e.g., checking if Depth > 50m). Data is tagged as HEALTHY or CRITICAL based on this check.
  
4. isualization: The pipeline generates a Scatter Plot (Sensor vs. Time) where valid data is shown in Blue and failures are highlighted in Red.
     
🛠️ Failure Scenarios Handled :

• Sensor Spikes: Anomalies like the 99.9m "Ghost Dive" are caught by the Threshold Filter.

• Temporal Drift: Asynchronous sampling rates are resolved through Nearest-Neighbor Matching.

• Data Loss: Out-of-phase hardware or packet loss triggers Status Tagging (CRITICAL) to engage fail-safe modes.

📝 Assumptions

• The system clock is synchronized, and timestamps always move forward.

• Sensor sampling rates (10 Hz and 2 Hz) remain consistent without "jitter".

• A 50m limit is a hard physical boundary for the current mission environment.

📝 Limitations

• Real-Time Transition: Moving from "Batch" processing of files to live data streaming.


• Failure Redundancy: Improving logic so the system doesn't pair "stale" data if a sensor drops to 0 Hz.


• Signal Smoothing: Implementing filters like a Kalman Filter or Moving Average to replace hard-coded thresholds.

# Quadruped Multi-Sensor Data Pipeline (Task 2 Complete) 

## 🏗️ System Architecture
The system is built as a modular, 4-layer stack designed for high-reliability robotic platforms. It follows the **Separation of Concerns** principle by decoupling raw data acquisition from failure intelligence.

### 📁 Modular Structure
- **Core/**: Contains `fid.py` (Failure Intelligence Discovery). This is the hardware-agnostic brain that processes variance and validates sensor states.
- **Drivers/**: Contains `pipeline_sim.py` and `sensors.py`. This layer manages data generation and simulates raw hardware feeds.
- **Logs/**: Stores JSON-formatted telemetry for post-mission audit and anomaly tracking.

---

## 🚀 Key Features
### 1. Failure Intelligence (Phase 3 & 4)
- **Trend Detection:** Uses a moving window to calculate IMU Z-axis variance, distinguishing between steady-state and dynamic movement.
- **Robustness Layer:** Specifically designed to handle "Stale Data" (via 500ms timeouts) and "Missing Data" (via null-value guards).

### 2. Multi-Rate Sensor Logic
- **IMU (10 Hz):** High-frequency processing for rapid stability detection.
- **Depth (2 Hz):** Medium-frequency terrain awareness to validate IMU trends.
- **Validation Logic:** Logic-gate check (e.g., IMU Stable + Depth Change = Sensor Issue).

### 3. Structured Telemetry (Phase 5)
- Standardized output using a formal `robot_state` dictionary with ISO-8601 timestamps for real-time monitoring and database compatibility.

---

## 🛠️ Hardware Readiness
While currently running on a simulated feed, the architecture is **Integration-Ready**. The logic in `Core/FID.py` can be deployed directly to an embedded platform (like STM32/ESP32) by simply swapping the `Drivers/` layer with actual I2C/SPI sensor libraries.
