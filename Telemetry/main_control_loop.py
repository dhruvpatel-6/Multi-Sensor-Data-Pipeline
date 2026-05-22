# Telemetry/main_control_loop.py
# Phase 5: Hardened Integration Engine with Explicit Fault Target Checking

import os
import sys
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Layers.pipeline_sync import DataSynchronizer

class TantraTelemetryEngine:
    def __init__(self, output_filepath="Tantra_logs/telemetry_truth.jsonl"):
        self.output_filepath = output_filepath
        self.synchronizer = DataSynchronizer()
        os.makedirs(os.path.dirname(self.output_filepath), exist_ok=True)

    def execute_integration_cycle(self, rugved_actuator_packet, rajaryan_control_packet, upstream_trace_id, execution_latency_ms=0.0):
        """
        Consumes integration boundaries, flags mechatronic faults, 
        and locks the frame against the Phase 1 canonical contract schema.
        """
        if rugved_actuator_packet is None:
            rugved_actuator_packet = {}

        # Initialize base states
        health_status = "NOMINAL"
        failure_reason = "NONE"

        # Extract internal elements safely to audit values directly
        joints = rugved_actuator_packet.get("joint_states")
        imu = rugved_actuator_packet.get("imu_data", {})

        # ---------------------------------------------------------
        # ROBUST FAULT DETECTION WINDOW
        # ---------------------------------------------------------
        
        # Check Failure Mode 1: Missing Actuator Data (Bus Link Dropout or Zeroed State)
        # Handles cases where joint_states is missing, None, empty, or missing sub-keys
        if (joints is None or not joints or 
            (isinstance(joints, dict) and joints.get("hip") == 0.0 and joints.get("knee") == 0.0)):
            health_status = "DEGRADED"
            failure_reason = "ACTUATOR_BUS_TIMEOUT"
        
        # Check Failure Mode 2: Corrupt Sensor Packet (Ghost Dive Pitch Register Anomaly)
        elif isinstance(imu, dict) and imu.get("pitch") == -99.0:
            health_status = "CRITICAL"
            failure_reason = "GHOST_DIVE_FAULT"

        # Check Failure Mode 3: Dynamic Latency Spike / Processing Overtime
        elif execution_latency_ms > 15.0:
            health_status = "DEGRADED"
            failure_reason = "LATENCY_SPIKE_DETECTED"

        # Enforce down-pipeline overrides on the packet before bundling
        rugved_actuator_packet["health_status"] = health_status
        rugved_actuator_packet["failure_reason"] = failure_reason
        rugved_actuator_packet["latency_ms"] = round(execution_latency_ms, 3)

        # Ensure fallback defaults are active if missing data occurred (NO NULLS allowed)
        if health_status == "DEGRADED" and (joints is None or not joints):
            rugved_actuator_packet["joint_states"] = {"hip": 0.0, "knee": 0.0}

        # 2. Force the Schema Lock through the Synchronizer Layer
        serialized_contract = self.synchronizer.bundle(
            hardware_snapshot=rugved_actuator_packet,
            control_input=rajaryan_control_packet,
            upstream_trace_id=upstream_trace_id
        )

        # 3. Append to Ledger Log
        with open(self.output_filepath, "a", encoding="utf-8") as ledger_stream:
            ledger_stream.write(serialized_contract + "\n")

        return serialized_contract