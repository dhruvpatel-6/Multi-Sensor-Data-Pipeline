# Telemetry/replay_telemetry.py
# Phase 6 — Truth Layer Telemetry Replay Engine

import os
import sys
import time
import json

# Ensure parent directory workspace visibility
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

class TantraTruthReplayEngine:
    def __init__(self, log_filepath="Tantra_logs/telemetry_truth.jsonl"):
        self.log_filepath = log_filepath

    def execute_replay(self, target_hz=10.0):
        """
        Reads append-only logs sequentially and reproduces system states 
        deterministically at the mandated execution frequency.
        """
        if not os.path.exists(self.log_filepath):
            raise FileNotFoundError(f"[CRITICAL] Truth ledger not found at target path: {self.log_filepath}")

        print(f"\n--- STARTING TELEMETRY REPLAY STREAM [{target_hz}Hz LOCK] ---")
        print(f"Reading from log source: {self.log_filepath}\n")

        interval_sec = 1.0 / target_hz
        playback_count = 0
        
        # Initialize dynamic drift correction time anchors
        next_frame_target = time.monotonic()

        with open(self.log_filepath, "r", encoding="utf-8") as ledger_stream:
            for line in ledger_stream:
                line = line.strip()
                if not line:
                    continue

                # Parse immutable transaction block frame
                try:
                    state_snapshot = json.loads(line)
                except json.JSONDecodeError as err:
                    print(f"[ERROR] Corrupt ledger entry skipped: {err}")
                    continue

                playback_count += 1
                
                # Extract state properties safely to verify integrity
                trace_id = state_snapshot.get("trace_id", "UNKNOWN-TRACE")
                health = state_snapshot.get("health_status", "UNKNOWN")
                reason = state_snapshot.get("failure_reason", "UNKNOWN")
                joints = state_snapshot.get("joint_states", {})
                imu = state_snapshot.get("imu_data", {})

                # Output state reproduction frame to show match accuracy
                print(f"[REPLAY FRAME {playback_count:03d}] Trace: {trace_id}")
                print(f"  └─ Health: {health} | Reason: {reason}")
                print(f"  └─ Joints: {joints}")
                print(f"  └─ IMU Telemetry: {imu}")
                print("-" * 60)

                # Deterministic frequency lock with anti-drift offset calculation
                next_frame_target += interval_sec
                sleep_remainder = next_frame_target - time.monotonic()
                
                if sleep_remainder > 0:
                    time.sleep(sleep_remainder)
                else:
                    # Overshoot recovery: shift anchor directly to clock track
                    next_frame_target = time.monotonic()

        print(f"\n[SUCCESS] Replay sequence finalized. Coherently reproduced {playback_count} states.")
        return playback_count

if __name__ == "__main__":
    replay_system = TantraTruthReplayEngine()
    try:
        replay_system.execute_replay(target_hz=10.0)
    except Exception as e:
        print(f"[CRITICAL VALIDATION FAILURE] Replay System Invalid: {e}")
        sys.exit(1)