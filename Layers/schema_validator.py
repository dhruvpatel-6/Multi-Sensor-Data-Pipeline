import json
import time

class SchemaValidator:
    """Strict deterministic schema enforcement for robot_state."""
    
    # Canonical field structure
    CANONICAL_LEGS = ["FRONT_LEFT", "FRONT_RIGHT", "REAR_LEFT", "REAR_RIGHT"]
    CANONICAL_JOINTS = ["HIP", "KNEE"]
    VALID_HEALTH_STATUSES = ["NOMINAL", "DEGRADED", "CRITICAL"]
    
    @staticmethod
    def get_empty_state():
        """Returns a guaranteed valid empty robot_state."""
        return {
            "trace_id": "00000000",
            "timestamp": time.time(),
            "joint_states": {
                leg: {joint: 0.0 for joint in SchemaValidator.CANONICAL_JOINTS}
                for leg in SchemaValidator.CANONICAL_LEGS
            },
            "torque_outputs": {leg: 0.0 for leg in SchemaValidator.CANONICAL_LEGS},
            "imu_data": {
                "pitch": 0.0,
                "roll": 0.0,
                "accel_z": 9.81
            },
            "contact_state": [False, False, False, False],
            "health_status": "NOMINAL",
            "failure_reason": "NONE",
            "latency_ms": 0.0
        }
    
    @staticmethod
    def validate(robot_state):
        """
        Validates robot_state against canonical schema.
        Returns: (is_valid: bool, errors: list[str])
        """
        errors = []
        
        if not isinstance(robot_state, dict):
            return False, ["robot_state must be a dictionary"]
        
        # 1. Check all required top-level fields exist
        required_fields = [
            "trace_id", "timestamp", "joint_states", "torque_outputs",
            "imu_data", "contact_state", "health_status", "failure_reason", "latency_ms"
        ]
        for field in required_fields:
            if field not in robot_state:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # 2. Validate trace_id
        trace_id = robot_state.get("trace_id")
        if not isinstance(trace_id, str) or len(trace_id) != 8:
            errors.append(f"trace_id must be 8-char string, got: {trace_id}")
        
        # 3. Validate timestamp
        timestamp = robot_state.get("timestamp")
        if not isinstance(timestamp, (int, float)) or timestamp <= 0:
            errors.append(f"timestamp must be positive number, got: {timestamp}")
        
        # 4. Validate joint_states
        joint_states = robot_state.get("joint_states")
        if not isinstance(joint_states, dict):
            errors.append("joint_states must be dictionary")
        else:
            # Check all legs present
            for leg in SchemaValidator.CANONICAL_LEGS:
                if leg not in joint_states:
                    errors.append(f"Missing leg in joint_states: {leg}")
                else:
                    leg_data = joint_states[leg]
                    if not isinstance(leg_data, dict):
                        errors.append(f"joint_states[{leg}] must be dictionary")
                    else:
                        # Check all joints present
                        for joint in SchemaValidator.CANONICAL_JOINTS:
                            if joint not in leg_data:
                                errors.append(f"Missing joint {joint} in leg {leg}")
                            else:
                                val = leg_data[joint]
                                if not isinstance(val, (int, float)):
                                    errors.append(f"joint_states[{leg}][{joint}] must be numeric")
            
            # Reject extra legs
            for leg in joint_states:
                if leg not in SchemaValidator.CANONICAL_LEGS:
                    errors.append(f"Unknown leg in joint_states: {leg}")
        
        # 5. Validate torque_outputs
        torque_outputs = robot_state.get("torque_outputs")
        if not isinstance(torque_outputs, dict):
            errors.append("torque_outputs must be dictionary")
        else:
            if set(torque_outputs.keys()) != set(SchemaValidator.CANONICAL_LEGS):
                errors.append(f"torque_outputs legs mismatch. Expected {SchemaValidator.CANONICAL_LEGS}, got {list(torque_outputs.keys())}")
            for leg, val in torque_outputs.items():
                if not isinstance(val, (int, float)):
                    errors.append(f"torque_outputs[{leg}] must be numeric")
        
        # 6. Validate imu_data
        imu_data = robot_state.get("imu_data")
        if not isinstance(imu_data, dict):
            errors.append("imu_data must be dictionary")
        else:
            required_imu_fields = ["pitch", "roll", "accel_z"]
            for field in required_imu_fields:
                if field not in imu_data:
                    errors.append(f"Missing imu_data field: {field}")
                elif not isinstance(imu_data[field], (int, float)):
                    errors.append(f"imu_data[{field}] must be numeric")
            
            # Reject extra IMU fields
            for field in imu_data:
                if field not in required_imu_fields:
                    errors.append(f"Unknown imu_data field: {field}")
        
        # 7. Validate contact_state
        contact_state = robot_state.get("contact_state")
        if not isinstance(contact_state, list):
            errors.append("contact_state must be list")
        else:
            if len(contact_state) != 4:
                errors.append(f"contact_state must have exactly 4 elements, got {len(contact_state)}")
            else:
                for i, val in enumerate(contact_state):
                    if not isinstance(val, bool):
                        errors.append(f"contact_state[{i}] must be boolean, got {type(val)}")
        
        # 8. Validate health_status
        health_status = robot_state.get("health_status")
        if health_status not in SchemaValidator.VALID_HEALTH_STATUSES:
            errors.append(f"health_status must be one of {SchemaValidator.VALID_HEALTH_STATUSES}, got: {health_status}")
        
        # 9. Validate failure_reason
        failure_reason = robot_state.get("failure_reason")
        if not isinstance(failure_reason, str):
            errors.append(f"failure_reason must be string, got {type(failure_reason)}")
        
        # 10. Validate latency_ms
        latency_ms = robot_state.get("latency_ms")
        if not isinstance(latency_ms, (int, float)):
            errors.append(f"latency_ms must be numeric, got {type(latency_ms)}")
        elif latency_ms < 0:
            errors.append(f"latency_ms must be non-negative, got {latency_ms}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def to_json(robot_state):
        """
        Converts validated robot_state to deterministic JSON string.
        Ensures field order and no extra data.
        """
        is_valid, errors = SchemaValidator.validate(robot_state)
        if not is_valid:
            raise ValueError(f"Cannot serialize invalid robot_state: {errors}")
        
        # Force canonical field order
        ordered = {
            "trace_id": robot_state["trace_id"],
            "timestamp": robot_state["timestamp"],
            "joint_states": robot_state["joint_states"],
            "torque_outputs": robot_state["torque_outputs"],
            "imu_data": robot_state["imu_data"],
            "contact_state": robot_state["contact_state"],
            "health_status": robot_state["health_status"],
            "failure_reason": robot_state["failure_reason"],
            "latency_ms": robot_state["latency_ms"]
        }
        
        return json.dumps(ordered, sort_keys=False, separators=(',', ':'))
