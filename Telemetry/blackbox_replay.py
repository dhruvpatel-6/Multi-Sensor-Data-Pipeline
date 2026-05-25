# Telemetry/blackbox_replay.py
import os
import sys
import time
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

class QuadrupedBlackboxReplay:
    def __init__(self, log_filepath="Logs/quadruped_telemetry_truth.jsonl"):
        self.log_filepath = log_filepath

    def execute_replay(self, target_hz=10.0):
        if not os.path.exists(self.log_filepath):
            raise FileNotFoundError(f"Log source missing at: {self.log_filepath}")

        print(f"\n--- INITIATING BLACKBOX STREAM REPLAY [{target_hz}Hz LOCK] ---")
        interval_sec = 1.0 / target_hz
        playback_count = 0
        next_frame_target = time.monotonic()

        with open(self.log_filepath, "r", encoding="utf-8") as ledger_stream:
            for line in ledger_stream:
                line = line.strip()
                if not line:
                    continue

                try:
                    state_snapshot = json.loads(line)
                except json.JSONDecodeError:
                    continue

                playback_count += 1
                trace_id = state_snapshot.get("trace_id", "UNKNOWN-TRACE")
                health = state_snapshot.get("health_status", "UNKNOWN")
                reason = state_snapshot.get("failure_reason", "UNKNOWN")

                print(f"[FRAME {playback_count:03d}] Trace: {trace_id} | Health: {health} | Reason: {reason}")

                next_frame_target += interval_sec
                sleep_remainder = next_frame_target - time.monotonic()
                if sleep_remainder > 0:
                    time.sleep(sleep_remainder)
                else:
                    next_frame_target = time.monotonic()

        print(f"\n[SUCCESS] Replay completed. Reconstructed {playback_count} historical frames.")
        return playback_count
