📑 REVIEW_PACKET.md: Real-Time Telemetry & Failure Intelligence

Candidate: Dhruv Patel 

Project: Robotics Quadruped Data Layer (Task 2) 

Status: Transitioned to Continuous Pipeline (Phase 5 Complete)

1. System Overview

The system has been upgraded from a file-based batch processor to a Continuous Real-Time Telemetry Pipeline. This architecture serves as the "nervous system" for the robot, ensuring that control systems receive high-frequency, synchronized, and validated sensor data.

Architecture Flow:

Ingestion: Simulated 10Hz live sensor feed (IMU, Depth, and Contact).
Synchronization: Multi-rate sensor alignment using nearest-neighbor timestamping.
Intelligence Layer: Real-time analysis for drift, spikes, and data staleness.
Structured Output: Standardized JSON state objects for downstream control integration.

2. Sensor Coverage & Fusion 

Unlike previous iterations, this pipeline now fully integrates all three required sensor streams to provide system-level awareness:

IMU ($Z$-Axis): Monitored at 10Hz for stability and acceleration trends.
Depth (Ultrasonic/LiDAR): Integrated for terrain mapping and obstacle detection.
Contact (Binary State): Now used in the pipeline to validate IMU and Depth readings (e.g., confirming "IN_AIR" status vs ground distance).

3. Failure Intelligence Logic

The Failure Intelligence Logic (FID) serves as the decision-making core of the pipeline, transitioning the system from simple data collection to active robot-state awareness. It processes synchronized sensor inputs to identify and flag operational risks through the following logic:

Sensor Spike Detection: The system monitors the depth stream for physically impossible readings, such as the 99.9m "Ghost Dive" spike, and immediately triggers a CRITICAL status to prevent erratic control responses.

IMU Trend & Stability Analysis: By calculating the variance of $Z$-axis acceleration over a sliding window, the logic detects mechanical instability or excessive vibration, shifting the health status to DEGRADED if thresholds are breached.

Stale Data & Latency Monitoring: A high-frequency heartbeat check ensures that data packets arrive within a 500ms window; exceeding this threshold flags a STALE_DATA_TIMEOUT, indicating a communication or simulator lag.

Multi-Sensor Correlation: The system validates movement by cross-referencing sensors. For instance, a stable IMU paired with a sudden depth change is flagged as a SENSOR_CONFLICT, whereas both sensors changing simultaneously confirms real robotic movement.

Data Integrity Protection: The logic includes guards for missing IMU, Depth, or Contact packets, ensuring the pipeline returns a MISSING_DATA warning rather than crashing the control loop.

4. Output Data Schema

To ensure consistency and prevent pipeline bugs, the output is strictly defined as a standardized robot_state object:

{
  "timestamp": "ISO-8601 String",
  "imu": {
    "accel_z": "float",
    "variance": "float"
  },
  "depth": "float",
  "contact": "STRING (GROUNDED/IN_AIR)",
  "health_status": "STRING (HEALTHY/DEGRADED/CRITICAL)",
  "failure_reason": "STRING (NOMINAL/ERROR_TYPE)"
}

5. Verification & Testing

The pipeline was stress-tested by injecting a 99.9m sensor spike. The system successfully:

Identified the spike in real-time.

Correlated it with stable IMU data to confirm it was a sensor issue rather than real movement.

Updated the health_status to CRITICAL within one cycle (100ms).