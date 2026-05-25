# Telemetry/state_machine.py
import logging

class QuadrupedStateMachine:
    # Define rigid, immutable execution state spaces
    STATES = ["BOOT", "NOMINAL", "WALKING", "RECOVERY", "UNSTABLE", "SAFE_MODE", "EMERGENCY_STOP"]

    def __init__(self, initial_state="BOOT"):
        self._current_state = initial_state if initial_state in self.STATES else "BOOT"
        
        # Explicit transition allowance mapping matrix
        self._transition_matrix = {
            "BOOT": ["NOMINAL", "EMERGENCY_STOP"],
            "NOMINAL": ["WALKING", "UNSTABLE", "SAFE_MODE", "EMERGENCY_STOP"],
            "WALKING": ["NOMINAL", "UNSTABLE", "SAFE_MODE", "EMERGENCY_STOP"],
            "UNSTABLE": ["RECOVERY", "SAFE_MODE", "EMERGENCY_STOP"],
            "RECOVERY": ["NOMINAL", "UNSTABLE", "SAFE_MODE", "EMERGENCY_STOP"],
            "SAFE_MODE": ["NOMINAL", "EMERGENCY_STOP"],
            "EMERGENCY_STOP": []  # Terminal state lock down
        }
        
        # Setup clean standard internal logging format
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("StateMachine")

    @property
    def current_state(self) -> str:
        return self._current_state

    def determine_severity(self, state: str) -> str:
        """Determines tracking severity levels for Phase 3 logs."""
        if state in ["UNSTABLE", "SAFE_MODE"]:
            return "WARN"
        elif state == "EMERGENCY_STOP":
            return "CRITICAL"
        return "INFO"

    def transit(self, target_state: str, trigger_reason: str) -> tuple[bool, str]:
        """
        Executes a deterministic state transition.
        Rejects invalid path sequences cleanly with no hidden drift.
        """
        if target_state not in self.STATES:
            err_msg = f"Rejected shift: Target state '{target_state}' does not exist within standard space."
            self.logger.error(err_msg)
            return False, err_msg

        if target_state in self._transition_matrix[self._current_state]:
            previous_state = self._current_state
            self._current_state = target_state
            
            log_entry = f"STATE_TRANSITION: [{previous_state}] ──({trigger_reason})──> [{target_state}]"
            self.logger.info(log_entry)
            return True, log_entry
        else:
            err_msg = f"VIOLATION REJECTED: Illegal link attempt from [{self._current_state}] directly to [{target_state}]."
            self.logger.warning(err_msg)
            return False, err_msg