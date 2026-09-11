# 🤖 Quadruped Multi-Sensor Telemetry & Failure Intelligence Pipeline

**A real-time, fault-aware telemetry backbone for a physical quadruped robotics prototype** — built to watch the robot's vitals, catch failures before they cascade, and give operators a live view of what's happening on hardware.

`Data Schema Standard: v3.0.0-Truth` · `Platform Iteration: v1.0.0-Prototype`

---

## 📌 What This Is

This is the telemetry and observability layer for a 12-actuator quadruped robot — not the motion controller itself, but the system that watches it: streaming sensor state off the hardware, validating it against a strict schema, detecting anomalies in real time, recording every session for replay, and surfacing it all on a live dashboard.

---

## 🏗️ Physical Platform

The telemetry pipeline runs on top of real hardware, not just simulation:

| Subsystem | Detail |
|---|---|
| **Compute** | NVIDIA Jetson Orin Nano — runs inverse kinematics and `analytics_worker.py` |
| **Real-time control** | C++ RT-Preempt kernel, 5 ms deterministic control loop |
| **Actuators** | 12× CubeMars AK80-9 BLDC actuators (3 per leg), daisy-chained on a 1 Mbps CAN-bus |
| **Sensors** | Central 9-axis IMU (BNO055) · 12× joint strain gauges (torque) · 12× local actuator thermistors · 4× foot-contact FSRs |
| **Power** | 6S 22.2V 5000mAh LiPo → dual-rail buck regulation (5V/5A for compute, 12V/4A for cooling) |
| **Safety** | Spine-mounted optocoupled E-stop — hard-wired motor power cut, software-triggered, active in under 15 ms |
| **Comms** | CAN-bus (actuators) + SPI/I2C (IMU, thermistors) into the Ecosystem Gateway Bus (TCP ports 5555/5556) |

---

## 🔄 Data Flow

```
Physical Sensors (IMU · Strain Gauges · Thermistors · Foot FSRs)
        │
        ▼
sensor_stream.py  ──[HardwareAbstractionLayer / Ecosystem Gateway]──▶  Port 5555
        │
        ▼
analytics_worker.py   (Port 5556)
   ├── Schema contract validation (v3.0.0-Truth)
   ├── Anomaly / latency-deadline detection
   └── Session recording ──▶ quadruped_session_recording.jsonl
        │
        ▼
visualization/view_dashboard.py   (Streamlit, port 8501)
```

Both `sensor_stream.py` and `analytics_worker.py` run as independent processes and can be launched together via `run_pipeline.ps1`, which also brings up the dashboard automatically.

---

## 🚀 Key Features

### 1. Schema-Enforced Telemetry
Every frame is validated against a formal canonical contract (`schema/canonical_telemetry_v3.json`) covering `health_status`, `control_state`, `locomotion_state`, `terrain_state`, `actuation_state`, and `system_health` — with a required `trace_id` for deterministic log replay chaining. Malformed or off-contract frames are rejected before they can pollute downstream state.

### 2. Deterministic, Reproducible Data Generation
`sensor_stream.py` seeds both `random` and `numpy` (`RANDOM_SEED = 42`) so simulated/injected sensor behavior is exactly reproducible across runs — essential for regression-testing failure scenarios rather than chasing a bug that only happened once.

### 3. Full Session Recording
Every run is logged frame-by-frame to `quadruped_session_recording.jsonl`, giving a complete, replayable record of exactly what the robot reported during a session — for post-mission audit or reproducing a fault offline.

### 4. HMAC-Based Command Verification
`security_guard.py` provides HMAC-SHA256 signature verification (`verify_token`) for securing API/socket commands, so a command's authenticity can be checked before it's trusted.

### 5. Live Operator Dashboard
`visualization/view_dashboard.py` (Streamlit, port 8501) gives a live cockpit view of the pipeline's telemetry stream while it's running.

### 6. Hardware-Grade Safety Design
The E-stop path is hard-wired at the power-distribution level, not just a software flag — a triggered stop cuts motor power directly, independent of whether the compute stack is still responsive.

---

## 🛠️ Failure Scenarios Handled

- **Sensor spikes / out-of-range readings** — caught by schema and threshold validation before reaching analytics logic
- **Malformed or off-contract frames** — rejected at the `v3.0.0-Truth` schema gate
- **Actuator/thermal stress** — joint thermistors and strain gauges feed directly into the telemetry stream for real-time monitoring
- **Power-level faults** — hardware E-stop cuts actuator power independently of software state

---

## 📁 Project Structure

```
sensor_stream.py            # Edge publisher — reads/simulates sensor data, streams JSON frames
analytics_worker.py         # Consumes the stream, validates schema, detects anomalies, records session
HardwareAbstractionLayer.py # Ecosystem Gateway — socket-level abstraction between publisher and worker
security_guard.py           # HMAC-SHA256 command/token verification
schema/
  canonical_telemetry_v3.json     # Formal JSON Schema for the telemetry contract
  unified_telemetry_schema.json
visualization/
  view_dashboard.py         # Streamlit live dashboard
tests/
  test_runtime.py           # Schema presence, auth verification, session-log integrity checks
review_packets/
  REVIEW_PACKET.md          # Full physical + software architecture handover doc
  INTEGRATION_NOTES.md      # Mechanical/electrical/bus assembly protocols
  BOM_Quadruped robot.pdf
  physical prototype_report.pdf
run_pipeline.ps1            # One-command launch: sensor stream + analytics worker + dashboard
quadruped_session_recording.jsonl   # Recorded telemetry sessions
```

---

## 📊 Current Status & Honest Limitations

- ✅ Schema validation, deterministic data generation, session recording, and HMAC command-verification logic are implemented and covered by `tests/test_runtime.py`.
- ✅ Full physical hardware architecture (compute, power, CAN-bus, actuators, sensors, E-stop) is documented in `review_packets/`.
- ⚠️ `security_guard.py`'s HMAC verification exists as a standalone, tested module but is **not yet wired into** the live `sensor_stream.py` / `analytics_worker.py` socket connections — currently anything that can reach ports 5555/5556 can still attach without a token check. Wiring it into the actual connection handshake is the natural next step.
- ⚠️ The HMAC key in `security_guard.py` is currently a hardcoded constant in source rather than an environment variable/secret — fine for a closed prototype, but should move out of source control before anything is shared or deployed more broadly.
- ⚠️ No TLS/encryption on the socket transport — the auth layer (once wired in) verifies identity, it doesn't encrypt telemetry in transit.

---

## 🗺️ Roadmap

- [ ] Wire `security_guard.verify_token` into the actual HAL/analytics socket handshake
- [ ] Move the HMAC secret out of source and into an environment variable
- [ ] TLS on the socket transport once it's used beyond a single machine
- [ ] Migrate the transport layer to ROS 2 for native multi-subscriber support and automatic reconnection
- [ ] Bring in Gazebo-simulated sensor feeds as a drop-in replacement for the synthetic generator once the above hardening is complete
- [ ] Expand `tests/test_runtime.py` into full end-to-end socket-level integration tests

---

## 🧪 Running the Tests

```bash
pip install pytest
pytest tests/ -v
```

## ▶️ Running the Pipeline

```powershell
./run_pipeline.ps1
```

This launches the sensor stream (port 5555), the analytics worker (port 5556), and the Streamlit dashboard (port 8501) in sequence.

---

## 📝 Assumptions

- System clock is synchronized and timestamps move strictly forward.
- The CAN-bus and I2C/SPI sensor buses deliver data at their documented rates without unmodeled jitter.
- `RANDOM_SEED = 42` is intentional for reproducibility during development/testing and should be revisited before any tuning against live hardware noise characteristics.
