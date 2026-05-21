# Layers/pipeline_sync.py
# Phase 3 Hardened Trace Propagation Pipeline

import json
import time

class DataSynchronizer:
    def __init__(self):
        pass

    def bundle(self, rugved_hardware, rajaryan_control, upstream_trace_id):
        """
        Phase 3 Core Rule: Accepts a strict upstream trace_id.
        Propagates the exact token without regeneration or mutation.
        """
        # Extract 12-DOF joint structures safely (HIP, KNEE)
        raw_joints = rugved_hardware.get("joint_states", {}) if isinstance(rugved_hardware, dict) else {}
        joint_states = {
            "FRONT_LEFT": {
                "HIP": float(raw_joints.get("FRONT_LEFT", {}).get("HIP", 0.0)),
                "KNEE": float(raw_joints.get("FRONT_LEFT", {}).get("KNEE", 0.0))
            },
            "FRONT_RIGHT": {
                "HIP": float(raw_joints.get("FRONT_RIGHT", {}).get("HIP", 0.0)),
                "KNEE": float(raw_joints.get("FRONT_RIGHT", {}).get("KNEE", 0.0))
            },
            "REAR_LEFT": {
                "HIP": float(raw_joints.get("REAR_LEFT", {}).get("HIP", 0.0)),
                "KNEE": float(raw_joints.get("REAR_LEFT", {}).get("KNEE", 0.0))
            },
            "REAR_RIGHT": {
                "HIP": float(raw_joints.get("REAR_RIGHT", {}).get("HIP", 0.0)),
                "KNEE": float(raw_joints.get("REAR_RIGHT", {}).get("KNEE", 0.0))
            }
        }

        raw_torques = rugved_hardware.get("torque_outputs", {}) if isinstance(rugved_hardware, dict) else {}
        torque_outputs = {
            "FRONT_LEFT": float(raw_torques.get("FRONT_LEFT", 0.0)),
            "FRONT_RIGHT": float(raw_torques.get("FRONT_RIGHT", 0.0)),
            "REAR_LEFT": float(raw_torques.get("REAR_LEFT", 0.0)),
            "REAR_RIGHT": float(raw_torques.get("REAR_RIGHT", 0.0))
        }

        raw_imu = rugved_hardware.get("imu", {}) if isinstance(rugved_hardware, dict) else {}
        imu_data = {
            "pitch": float(raw_imu.get("pitch", 0.0)),
            "roll": float(raw_imu.get("roll", 0.0)),
            "accel_z": float(raw_imu.get("accel_z", 9.81))
        }

        raw_contact = rugved_hardware.get("contact", [False, False, False, False])
        contact_state = [bool(x) for x in raw_contact[:4]]

        system_mode_str = rajaryan_control.get("system_mode", "STABILIZING") if isinstance(rajaryan_control, dict) else "STABILIZING"
        latency_val = rajaryan_control.get("latency_ms", 0.0) if isinstance(rajaryan_control, dict) else 0.0

        # Construct payload contract forcing trace_id to preserve incoming token explicitly
        robot_state = {
            "trace_id": str(upstream_trace_id),  # Strict pass-through lock
            "timestamp": float(time.time()),
            "joint_states": joint_states,
            "torque_outputs": torque_outputs,
            "imu_data": imu_data,
            "contact_state": contact_state,
            "health_status": str(rugved_hardware.get("status", "NOMINAL")), 
            "failure_reason": str(rugved_hardware.get("reason", "NONE")),
            "system_mode": str(system_mode_str),
            "latency_ms": float(latency_val)
        }

        return json.dumps(robot_state, sort_keys=True)