# Telemetry/fault_intelligence.py

class FailureCorrelationEngine:
    def __init__(self):
        pass

    def analyze_causal_chain(self, locomotion: dict, stability: dict, mechanical: dict, thermal: dict) -> dict:
        """
        Analyzes multi-developer sensor parameters to verify an unbroken causal failure line.
        Proves the physical relationship from environment to system trip.
        """
        # Tier 1: Extract Root Environmental Risk
        terrain = locomotion.get("terrain_type", "NOMINAL")
        gait = locomotion.get("gait_phase", "STATIC")
        is_high_risk_terrain = terrain in ["SLIPPERY_ICE", "UNEVEN_GRAVEL"]

        # Tier 2: Kinematic Balance Deviations
        stability_score = float(stability.get("stability_score", 100.0))
        tilt = stability.get("tilt_state", {})
        pitch = abs(float(tilt.get("pitch_rad", 0.0)))
        roll = abs(float(tilt.get("roll_rad", 0.0)))
        is_kinematically_unstable = stability_score < 50.0 or pitch > 0.4 or roll > 0.4

        # Tier 3: Structural Load Reactions
        stress_zones = mechanical.get("structural_stress_zones", [])
        loads = mechanical.get("actuator_load", {})
        max_load = max([float(v) for v in loads.values()]) if loads else 0.0
        has_structural_overload = max_load > 0.80 or (len(stress_zones) > 0 and "NONE" not in stress_zones)

        # Tier 4: Electrical Actuator Saturation limits
        sat_dict = thermal.get("motor_saturation", {}).get("FL", {}) # Focus on primary indicators
        knee_sat = float(sat_dict.get("knee", 0.0))
        is_motor_saturated = knee_sat > 0.85

        # Evaluate Cascading Connectivity Verification
        chain_broken = False
        evidence_logs = []

        if is_high_risk_terrain:
            evidence_logs.append(f"[ROOT CAUSE] High-hazard surface detected: {terrain}")
            if is_kinematically_unstable:
                evidence_logs.append(f"[KINEMATIC EFFECT] Balance lost. Stability dropped to {stability_score:.1f} (Pitch: {pitch:.2f} rad)")
                if has_structural_overload:
                    evidence_logs.append(f"[STRUCTURAL REACTION] Peak load hit {max_load:.2f} across active stress paths: {stress_zones}")
                    if is_motor_saturated:
                        evidence_logs.append(f"[ELECTRICAL CRITICALITY] Thermal knee saturation breached nominal thresholds: {knee_sat*100:.1f}%")
                    else:
                        chain_broken = True
                        evidence_logs.append("[CHAIN_BREAK] Structural load spike did not induce electrical saturation thresholds.")
                else:
                    chain_broken = True
                    evidence_logs.append("[CHAIN_BREAK] Kinematic deviation failed to cross structural stress limits.")
            else:
                chain_broken = True
                evidence_logs.append("[CHAIN_BREAK] Environmental hazard was absorbed cleanly by kinematic controller balance loops.")
        else:
            evidence_logs.append("[NOMINAL] Root environmental baselines operating within standard safe tolerances.")

        is_correlated_cascade = (is_high_risk_terrain and is_kinematically_unstable and has_structural_overload and is_motor_saturated)

        return {
            "is_correlated_cascade": is_correlated_cascade,
            "chain_broken": chain_broken,
            "correlation_depth": len(evidence_logs),
            "evidence_chain": evidence_logs,
            "summary_verdict": "CRITICAL_CAUSAL_CASCADE_PROVEN" if is_correlated_cascade else "STANDALONE_OR_NO_ANOMALY"
        }