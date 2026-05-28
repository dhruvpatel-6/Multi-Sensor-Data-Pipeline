1. Injected Fault: ACTUATOR_BUS_TIMEOUT

• Root System Severity: DEGRADED  

• Telemetry Layer Impact (system_health.schema_status): States drop to a DEGRADED verification posture.  

• Rajaryan Control Layer Impact (control_state): Automatically switches to SAFE_FALLBACK control mode and shifts the gait profile directly into a RECOVERY_PULSE configuration.  

• Rugved Actuator Layer Impact (actuation_state): Flags communication bus health explicitly as TIMEOUT_CRITICAL and throttles motor output down to a CURRENT_LIMITED protective envelope.  

• Replay Annotation Tag (meta.replay_status_annotation): Injects the deterministic tracking tag: FAULT_BUS_TIMEOUT_DEGRADED_PERFORMANCE.  



2. Injected Fault: GHOST_DIVE_FAULT

• Root System Severity: EMERGENCY_STOP   

• Telemetry Layer Impact (system_health.schema_status): Flags structural layout validation immediately as INVALID_STRUCTURE.  

• Rajaryan Control Layer Impact (control_state): Triggers a mandatory high-level control halt, locks target velocities at [0.0, 0.0, 0.0], sets the recovery status to SELF_RIGHTING, and forces a static STAND gait state.  

• Rugved Actuator Layer Impact (actuation_state): Broadlocks hardware actuation nodes into a defensive, immediate shutdown state: THERMAL_FAULT.  

• Replay Annotation Tag (meta.replay_status_annotation): Injects the deterministic tracking tag: CRITICAL_GHOST_DIVE_COMMAND_HALT.  



3. Injected Condition: NOMINAL_CLEAR

• Root System Severity: NOMINAL   

• Telemetry Layer Impact (system_health.schema_status): Re-establishes a clean, verified state: VALIDATED.  

• Rajaryan Control Layer Impact (control_state): Restores default path tracking profiles to POSITION mode and resumes standard operational TROTTING speed metrics.  

• Rugved Actuator Layer Impact (actuation_state): Clears warnings and restores the hardware bus communication links back to full OPERATIONAL capacity.  

• Replay Annotation Tag (meta.replay_status_annotation): Returns the tracking stream annotation to standard runtime parameters: LIVE_STREAM. 