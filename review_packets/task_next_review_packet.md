# 🏆 Review Packet & Handover Architecture Documentation
**System Specification Standard:** `v3.0.0-Truth` | **Author:** Robotics Engineering Team

---

## 1. Execution Architecture & Handover Summary
The Quadruped Reality Convergence Telemetry Core is a low-latency, deterministic multi-process data pipeline designed to manage live high-frequency telemetry streams from a 12-DoF quadruped platform.

The system uses a decoupled microservices architecture via non-blocking TCP loop sockets:
1. **`sensor_stream.py` (HAL Layer):** Simulates or plays back raw hardware registers (Thermistors, Torque Strain Grids, 9-Axis MEMS IMU, and sole FSR Contact Sensors) under variable network noise and timing jitter conditions.
2. **`analytics_worker.py` (Analytics Core):** Applies a moving-window sliding Z-score filter to calculate lateral drift anomalies and map dynamic stability degradation matrices on distinct terrain envelopes.
3. **`view_dashboard.py` (Streamlit UI Cockpit):** Serves as the UI observability plane, displaying loop timing, deadline breaches, and control system recovery logs.

---

## 2. Fast Deployment & Execution Instructions
### Prerequisites
Ensure your local Python environment has the baseline packages installed:
```bash
pip install numpy pandas streamlit pydantic

Running the System Pipeline
Execute the master PowerShell orchestrator to launch all concurrent backend microservices and the web dashboard layer simultaneously:

.\run_pipeline.ps1

Alternatively, launch the nodes in separate shell windows in order:

# Terminal 1: Hardware Abstraction Layer
python sensor_stream.py

# Terminal 2: Real-time Analytics Processor
python analytics_worker.py

# Terminal 3: Streamlit UI Frontend
streamlit run visualization/view_dashboard.py



Open your web browser and navigate to http://localhost:8501 to view the running observability core.


## 3.Integration & Trace Continuity Map:-
To prevent operational data siloing, this system establishes complete downstream data trace continuity across the enterprise pipeline:


[Quadruped HAL (sensor_stream.py)] 
         │ 
         ▼ (Port 5555: Canonical JSON Payload v3.0.0-Truth)
[Analytics Core (analytics_worker.py)]
         │
         ├──► [Control Core] --> Computes inverse kinematics gait duty cycles based on slip signatures
         ├──► [Simulation] -> Re-injects failure profiles into millions-scale episodic training runs
         │
         ▼ (Port 5556: Telemetry Packets + Calculated State Matrices)
[TANTRA Data Warehouse Warehouse Layer] --> Persists telemetry frames to terrain_profile.json for end-to-end auditability


## 4. API & Schema Specification
All network sockets and processing blocks strictly enforce the v3.0.0-Truth canonical schema standard.

Core Schema Contract Model (Pydantic Structure)

{
  "contract_version": "v3.0.0-Truth",
  "frame_idx": "Integer",
  "timestamp": "String (HH:MM:SS.mmm)",
  "target_deadline_ms": 5.0,
  "observed_latency_ms": "Float",
  "fault_injection_state": "String (NOMINAL | IMU_DRIFT_CORRUPTION | ACTUATOR_THERMAL_SATURATION | CONTACT_SENSOR_FAULT)",
  "terrain_context": {
    "terrain_id": "String",
    "traction_score": "Float (0.0 - 1.0)",
    "failure_probability": "Float",
    "recommended_gait": "String",
    "energy_cost_estimate": "Float"
  },
  "sensor_matrices": {
    "temperatures_c": "Array of 4/12 Floats",
    "torques_nm": "Array of 4/12 Floats",
    "imu_orientation": {"roll": "Float", "pitch": "Float"},
    "contact_sensor_vector": "Array of 4 Integers"
  }
}