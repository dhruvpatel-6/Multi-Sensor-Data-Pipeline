# Core/state_synchronizer.py
import json
import time
import os
from jsonschema import validate

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
SCHEMA_PATH = os.path.join(REPO_ROOT, "Telemetry", "Schema", "unified_telemetry_schema.json")

class QuadrupedStateSynchronizer:
    def __init__(self):
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        else:
            self.schema = None
            print(f"[WARNING] Schema file missing at {SCHEMA_PATH}. Disabling verification gate.")

    def bundle(self, locomotion_data: dict, mechanical_data: dict, stability_data: dict, thermal_data: dict, 
               trace_id: str, current_state: str, previous_state: str, transition_desc: str, severity: str = "INFO") -> str:
        
        locomotion = locomotion_data if isinstance(locomotion_data, dict) else {}
        mechanical = mechanical_data if isinstance(mechanical_data, dict) else {}
        stability = stability_data if isinstance(stability_data, dict) else {}
        thermal = thermal_data if isinstance(thermal_data, dict) else {}

        # ------------------------------------------------------------------
        # 1. STRUCTURAL LOCOMOTION MAPPING LAYOUT (ARYA OUTPUTS)
        # ------------------------------------------------------------------
        support_poly_in = locomotion.get("support_polygon", {}) if isinstance(locomotion.get("support_polygon"), dict) else {}
        support_polygon = {
            "vertex_count": int(support_poly_in.get("vertex_count", 4)),
            "coordinates_xy": support_poly_in.get("coordinates_xy", [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]),
            "contact_states": support_poly_in.get("contact_states", [1, 1, 1, 1])
        }
        locomotion_layer = {
            "gait_phase": str(locomotion.get("gait_phase", "STATIC_STANDBY")),
            "terrain_type": str(locomotion.get("terrain_type", "FLOWERBED_NOMINAL")),
            "support_polygon": support_polygon
        }

        # ------------------------------------------------------------------
        # 2. STRUCTURAL MECHANICAL MATRIX MAPPING LAYOUT (MANYA OUTPUTS)
        # ------------------------------------------------------------------
        actuator_load = mechanical.get("actuator_load", {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0})
        torque_reqs_in = mechanical.get("torque_requirements", {})
        torque_requirements = {}
        for leg in ["FL", "FR", "RL", "RR"]:
            leg_t = torque_reqs_in.get(leg, {}) if isinstance(torque_reqs_in, dict) and leg in torque_reqs_in else {}
            torque_requirements[leg] = {
                "abduction": float(leg_t.get("abduction", 0.0)),
                "hip": float(leg_t.get("hip", 0.0)),
                "knee": float(leg_t.get("knee", 0.0))
            }
        mechanical_structural_layer = {
            "actuator_load": {leg: float(actuator_load.get(leg, 0.0)) for leg in ["FL", "FR", "RL", "RR"]},
            "torque_requirements": torque_requirements,
            "structural_stress_zones": mechanical.get("structural_stress_zones", [])
        }

        # ------------------------------------------------------------------
        # 3. DYNAMIC KINEMATICS STABILITY MAPPING LAYOUT
        # ------------------------------------------------------------------
        tilt_in = stability.get("tilt_state", {})
        tilt_state = {
            "pitch_rad": float(tilt_in.get("pitch_rad", 0.0)) if isinstance(tilt_in, dict) else 0.0,
            "roll_rad": float(tilt_in.get("roll_rad", 0.0)) if isinstance(tilt_in, dict) else 0.0,
            "yaw_rad": float(tilt_in.get("yaw_rad", 0.0)) if isinstance(tilt_in, dict) else 0.0
        }
        slip_in = stability.get("slip_state", {})
        slip_ratio_in = slip_in.get("slip_ratio_per_leg", {}) if isinstance(slip_in, dict) else {}
        slip_state = {
            "is_slipping": bool(slip_in.get("is_slipping", False)) if isinstance(slip_in, dict) else False,
            "slip_ratio_per_leg": {leg: float(slip_ratio_in.get(leg, 0.0)) for leg in ["FL", "FR", "RL", "RR"]}
        }
        stability_metrics = {
            "com_position": [float(x) for x in stability.get("com_position", [0.0, 0.0, 0.0])],
            "tilt_state": tilt_state,
            "slip_state": slip_state,
            "stability_score": float(stability.get("stability_score", 100.0))
        }

        # ------------------------------------------------------------------
        # 4. ACTUATOR THERMAL/ELECTRICAL MAPPING LAYOUT
        # ------------------------------------------------------------------
        sat_in = thermal.get("motor_saturation", {})
        therm_in = thermal.get("thermal_state", {})
        motor_saturation = {}
        thermal_state = {}
        for leg in ["FL", "FR", "RL", "RR"]:
            leg_s = sat_in.get(leg, {}) if isinstance(sat_in, dict) and leg in sat_in else {}
            leg_th = therm_in.get(leg, {}) if isinstance(therm_in, dict) and leg in therm_in else {}
            motor_saturation[leg] = {
                "abduction": float(leg_s.get("abduction", 0.0)),
                "hip": float(leg_s.get("hip", 0.0)),
                "knee": float(leg_s.get("knee", 0.0))
            }
            thermal_state[leg] = {
                "abduction": float(leg_th.get("abduction", 25.0)),
                "hip": float(leg_th.get("hip", 25.0)),
                "knee": float(leg_th.get("knee", 25.0))
            }
        thermal_electrical_layer = {
            "motor_saturation": motor_saturation,
            "thermal_state": thermal_state
        }

        # ------------------------------------------------------------------
        # 5. ATOMIC FRAME ASSEMBLY WITH IMMUTABLE TRACEABILITY CONTINUITY
        # ------------------------------------------------------------------
        frame = {
            "trace_id": str(trace_id),
            "timestamp": float(time.time()),
            "subsystem_source": "DHRUV_CONTROL_CORE",
            "state_machine": {
                "current_state": str(current_state),
                "previous_state": str(previous_state),
                "state_transition": str(transition_desc),
                "severity_level": str(severity),
                "failure_state": {
                    "is_fault_active": current_state in ["UNSTABLE", "SAFE_MODE", "EMERGENCY_STOP"],
                    "failure_reason": "NONE" if current_state not in ["UNSTABLE", "SAFE_MODE", "EMERGENCY_STOP"] else transition_desc,
                    "error_code": 0 if current_state not in ["UNSTABLE", "SAFE_MODE", "EMERGENCY_STOP"] else 500
                }
            },
            # Explicit dict casting eliminates remaining Pylance editor warnings completely
            "locomotion_layer": dict(locomotion_layer),
            "mechanical_structural_layer": dict(mechanical_structural_layer),
            "stability_metrics": dict(stability_metrics),
            "thermal_electrical_layer": dict(thermal_electrical_layer)
        }

        # Final verification gate against schema specifications
        if self.schema is not None:
            validate(instance=frame, schema=self.schema)

        return json.dumps(frame)