import json
import hashlib
import sys
from datetime import datetime

class ReplayIntegrityEngine:
    def __init__(self, expected_version="2.0.0"):
        self.expected_version = expected_version
        self.expected_total_frames = 5
        self.schema_version_key = "schema_version" # Locked for compatibility

    def calculate_frame_hash(self, frame_data):
        """Generates a deterministic SHA-256 hash of the payload keys and values."""
        # Normalize by sorting keys to ensure deterministic hashing
        serialized = json.dumps(frame_data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def verify_replay_stream(self, file_path):
        print(f"=====================================================================")
        print(f" STARTING DETERMINISTIC REPLAY INTEGRITY INSPECTION                  ")
        print(f" Target Source: {file_path}                                         ")
        print(f" Expected Schema Version: v{self.expected_version}                   ")
        print(f"=====================================================================\n")

        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {"total_processed": 0, "status": "PASSED", "error_detected": "NONE"},
            "checks": {
                "schema_version_lock": "PASSED",
                "frame_count_validation": "PASSED",
                "payload_alteration_check": "PASSED",
                "sequence_continuity": "PASSED"
            },
            "failures_isolated": []
        }

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            report["summary"]["status"] = "FAILED"
            report["summary"]["error_detected"] = "FILE_NOT_FOUND"
            return report

        # 1. Frame Count Validation
        actual_count = len(lines)
        report["summary"]["total_processed"] = actual_count
        if actual_count != self.expected_total_frames:
            report["checks"]["frame_count_validation"] = "FAILED"
            reason = f"Frame count mismatch. Expected {self.expected_total_frames}, found {actual_count}."
            report["failures_isolated"].append({"type": "MISSING_OR_DUPLICATED_FRAMES", "reason": reason})
            report["summary"]["status"] = "CORRUPTED"

        previous_hash = None
        seen_trace_ids = set()
        expected_seq = 1

        for idx, line in enumerate(lines):
            try:
                frame = json.loads(line.strip())
            except json.JSONDecodeError:
                report["checks"]["payload_alteration_check"] = "FAILED"
                report["failures_isolated"].append({"type": "MALFORMED_JSON_PAYLOAD", "frame_index": idx})
                report["summary"]["status"] = "CORRUPTED"
                continue

            # 2. Schema Version Locking Check
            frame_version = frame.get("meta", {}).get("schema_version", "1.0.0")
            if frame_version != self.expected_version:
                report["checks"]["schema_version_lock"] = "FAILED"
                report["failures_isolated"].append({
                    "type": "SCHEMA_MISMATCH",
                    "frame_index": idx,
                    "reason": f"Expected version {self.expected_version}, got {frame_version}"
                })
                report["summary"]["status"] = "CORRUPTED"

            # 3. Duplicate Frame Tracking via Trace ID
            trace_id = frame.get("trace_id")
            if trace_id in seen_trace_ids:
                report["checks"]["sequence_continuity"] = "FAILED"
                report["failures_isolated"].append({
                    "type": "DUPLICATED_FRAME_DETECTED",
                    "trace_id": trace_id,
                    "frame_index": idx
                })
                report["summary"]["status"] = "CORRUPTED"
            seen_trace_ids.add(trace_id)

            # 4. Sequential Sequence Counter Verification
            current_seq = frame.get("meta", {}).get("sequence_number", 0)
            if current_seq != expected_seq:
                report["checks"]["sequence_continuity"] = "FAILED"
                report["failures_isolated"].append({
                    "type": "SEQUENCE_GAP_OR_JUMP",
                    "expected": expected_seq,
                    "actual": current_seq,
                    "frame_index": idx
                })
                report["summary"]["status"] = "CORRUPTED"
            expected_seq += 1

            # 5. Cryptographic Checksum Verification (Hash tracking)
            transmitted_hash = frame.get("meta", {}).get("frame_hash")
            # Remove hash field to replicate generation conditions
            pure_frame = frame.copy()
            if "meta" in pure_frame and "frame_hash" in pure_frame["meta"]:
                del pure_frame["meta"]["frame_hash"]
            
            calculated_hash = self.calculate_frame_hash(pure_frame)
            if transmitted_hash != calculated_hash:
                report["checks"]["payload_alteration_check"] = "FAILED"
                report["failures_isolated"].append({
                    "type": "ALTERED_PAYLOAD_CHECKSUM_MISMATCH",
                    "frame_index": idx,
                    "trace_id": trace_id,
                    "expected_hash": calculated_hash,
                    "received_hash": transmitted_hash
                })
                report["summary"]["status"] = "CORRUPTED"

        if len(report["failures_isolated"]) > 0 and report["summary"]["status"] == "PASSED":
            report["summary"]["status"] = "CORRUPTED"
            
        return report

# For active CLI execution proof
if __name__ == "__main__":
    engine = ReplayIntegrityEngine()
    # Path to test log target
    result = engine.verify_replay_stream("logs/processed_synced_logs.json")
    print(json.dumps(result, indent=2))