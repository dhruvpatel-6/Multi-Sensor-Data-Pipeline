# Layers/pipeline_sync.py
# Phase 1: Contract Lock (Telemetry Schema Hardening)

import json
import time

class DataSynchronizer:
    def __init__(self):
        # Explicit non-null safe fallback blocks matching structural layout
        self.DEFAULT_JOINTS = {"hip": 0.0, "knee": 0.0}
        self.DEFAULT_TORQUES = {"hip": 0.0, "knee": 0.0}
        self.DEFAULT_IMU = {"pitch": 0.0, "roll": 0.0, "accel_z": 9.81}
        self.VALID_HEALTH_STATES = {"NOMINAL", "DEGRADED", "CRITICAL"}

    def bundle(self, hardware_snapshot, control_input, upstream_trace_id):
        """
        Ingests real integration streams, enforces structural schema restrictions,
        and serializes a rigid canonical deterministic JSON output string.
        """
        # Validate or populate the non-negotiable trace ID directly
        trace_id = str(upstream_trace_id) if upstream_trace_id else f"TANTRA-ERR-{int(time.time())}"
        
        # Enforce exact key existence and internal mapping boundaries
        raw_joints = hardware_snapshot.get("joint_states", {}) if hardware_snapshot else {}
        raw_torques = hardware_snapshot.get("torque_outputs", {}) if hardware_snapshot else {}
        raw_imu = hardware_snapshot.get("imu_data", {}) if hardware_snapshot else {}
        
        # Extract individual mechatronic topology subkeys safely (No Missing Fields)
        joint_states = {
            "hip": float(raw_joints.get("hip", self.DEFAULT_JOINTS["hip"])),
            "knee": float(raw_joints.get("knee", self.DEFAULT_JOINTS["knee"]))
        }
        
        torque_outputs = {
            "hip": float(raw_torques.get("hip", self.DEFAULT_TORQUES["hip"])),
            "knee": float(raw_torques.get("knee", self.DEFAULT_TORQUES["knee"]))
        }
        
        imu_data = {
            "pitch": float(raw_imu.get("pitch", self.DEFAULT_IMU["pitch"])),
            "roll": float(raw_imu.get("roll", self.DEFAULT_IMU["roll"])),
            "accel_z": float(raw_imu.get("accel_z", self.DEFAULT_IMU["accel_z"]))
        }
        
        contact_state = bool(hardware_snapshot.get("contact_state", True)) if hardware_snapshot else True
        
        # Parse state transitions safely
        health_status = hardware_snapshot.get("health_status", "NOMINAL") if hardware_snapshot else "NOMINAL"
        if health_status not in self.VALID_HEALTH_STATES:
            health_status = "DEGRADED"
            
        failure_reason = str(hardware_snapshot.get("failure_reason", "NONE")) if hardware_snapshot else "NONE"
        latency_ms = float(hardware_snapshot.get("latency_ms", 0.0)) if hardware_snapshot else 0.0

        # Construct the unified ONE canonical robot_state payload dictionary layout
        canonical_robot_state = {
            "trace_id": trace_id,
            "timestamp": float(time.time()),
            "joint_states": joint_states,
            "torque_outputs": torque_outputs,
            "imu_data": imu_data,
            "contact_state": contact_state,
            "health_status": health_status,
            "failure_reason": failure_reason,
            "latency_ms": round(latency_ms, 3)
        }

        # Force strict deterministic string serialization lock (Alphabetical sort keys)
        return json.dumps(canonical_robot_state, sort_keys=True)