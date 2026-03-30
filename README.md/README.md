System Architecture (The Structure):

This section explains the "layers" of your software and the "types" of hardware it is designed to handle.

Modular Design: The system is built as a standalone, 4-layer stack that is "integration-ready" for future robotic platforms.

Multi-Rate Sensor Stack:

1] IMU: Operates at 10 Hz (High Frequency) as the primary timing reference.

2] Distance/Depth: Operates at 2 Hz (Medium Frequency) for terrain awareness.

3] Leak/Contact Sensors: Event-based binary sensors for internal safety and hull integrity.

Error Handling Layer: A dedicated module for injecting and detecting real-world issues like 99.9m spikes and IMU drift.

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
