import json
import time
from datetime import datetime

class ObservabilityEngine:
    def __init__(self):
        # Metrics Tracking Accumulators
        self.latency_records = []
        self.total_expected_frames = 0
        self.processed_frames = 0
        self.dropped_frames = 0
        self.schema_violations = 0
        self.anomaly_count = 0
        self.health_transitions = 0
        self.last_health_status = None
        self.total_replay_drift_ms = 0.0

    def process_session_telemetry(self, log_file_path):
        """Parses the active telemetry log stream to gather exact metrics."""
        try:
            with open(log_file_path, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return {"error": f"Target log {log_file_path} not found."}

        self.total_expected_frames = len(lines)
        expected_sequence = 1

        for line in lines:
            if not line.strip():
                continue
            
            try:
                frame = json.loads(line.strip())
            except json.JSONDecodeError:
                self.schema_violations += 1
                continue

            self.processed_frames += 1

            # 1. Track Latencies
            latency = frame.get("loop_latency_ms", 0.0)
            self.latency_records.append(latency)

            # 2. Track Dropped Frames via Sequence Jumping
            current_sequence = frame.get("meta", {}).get("sequence_number", expected_sequence)
            if current_sequence > expected_sequence:
                self.dropped_frames += (current_sequence - expected_sequence)
                expected_sequence = current_sequence
            expected_sequence += 1

            # 3. Track Anomaly Frequencies
            # Checks for terrain slips, electrical saturation, or critical stops
            if (frame.get("terrain_state", {}).get("slip_probability", 0.0) > 0.5 or 
                frame.get("health_status") == "EMERGENCY_STOP" or 
                frame.get("failure_reason") != "NONE"):
                self.anomaly_count += 1

            # 4. Track Schema Violations
            if frame.get("system_health", {}).get("schema_status") != "VALIDATED":
                self.schema_violations += 1

            # 5. Track Health Transitions
            current_health = frame.get("health_status", "NOMINAL")
            if self.last_health_status is not None and current_health != self.last_health_status:
                self.health_transitions += 1
            self.last_health_status = current_health

            # 6. Calculate Replay Time Drift
            # Measures delta between execution time tracking and target playback clock
            expected_cycle_time_ms = 4.0  # Target pipeline deadline
            drift = abs(latency - expected_cycle_time_ms)
            if drift > 0.5:  # Consider jitter greater than 0.5ms as operational drift
                self.total_replay_drift_ms += drift

    def generate_dashboard_json(self):
        """Compiles tracked metrics into a structured observability payload."""
        if not self.latency_records:
            return {"status": "NO_DATA_PROCESSED"}

        avg_latency = sum(self.latency_records) / len(self.latency_records)
        max_latency = max(self.latency_records)
        
        dashboard = {
            "dashboard_timestamp": datetime.utcnow().isoformat() + "Z",
            "pipeline_identity": "Quadruped-Observability-Backbone-v2",
            "runtime_performance_metrics": {
                "average_loop_latency_ms": round(avg_latency, 2),
                "maximum_loop_latency_ms": round(max_latency, 2),
                "target_deadline_ms": 4.0,
                "deadline_compliance_percentage": round((len([l for l in self.latency_records if l <= 4.0]) / len(self.latency_records)) * 100, 1)
            },
            "stream_integrity_metrics": {
                "total_frames_ingested": self.processed_frames,
                "dropped_frames_count": self.dropped_frames,
                "frame_loss_rate_percentage": round((self.dropped_frames / (self.processed_frames + self.dropped_frames)) * 100, 2) if (self.processed_frames + self.dropped_frames) > 0 else 0.0,
                "schema_validation_violations": self.schema_violations
            },
            "chronological_replay_drift": {
                "accumulated_replay_drift_ms": round(self.total_replay_drift_ms, 3),
                "average_drift_per_frame_ms": round(self.total_replay_drift_ms / self.processed_frames, 4) if self.processed_frames > 0 else 0.0
            },
            "behavioral_anomaly_metrics": {
                "isolated_anomaly_frequency": self.anomaly_count,
                "state_health_transitions": self.health_transitions,
                "terminal_health_state": self.last_health_status
            }
        }
        return dashboard

if __name__ == "__main__":
    engine = ObservabilityEngine()
    engine.process_session_telemetry("logs/processed_synced_logs.json")
    print(json.dumps(engine.generate_dashboard_json(), indent=2))