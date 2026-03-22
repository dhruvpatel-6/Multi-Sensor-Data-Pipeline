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
