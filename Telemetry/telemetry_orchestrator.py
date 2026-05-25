# Telemetry/telemetry_orchestrator.py
import os
import json
from Core.state_synchronizer import QuadrupedStateSynchronizer
from Telemetry.state_machine import QuadrupedStateMachine
from Telemetry.fault_intelligence import FailureCorrelationEngine

class QuadrupedTelemetryOrchestrator:
    def __init__(self):
        self.synchronizer = QuadrupedStateSynchronizer()
        self.state_machine = QuadrupedStateMachine(initial_state="BOOT")
        self.correlation_engine = FailureCorrelationEngine()
        
        self.state_machine.transit("NOMINAL", "Telemetry layer initial alignment verification completed")
        
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.truth_file_path = os.path.join(os.path.dirname(CURRENT_DIR), "quadruped_telemetry_truth.jsonl")

    def execute_integration_cycle(self, locomotion_data: dict, mechanical_data: dict, 
                                  stability_data: dict, thermal_data: dict, upstream_trace_id: str):
        previous_state = self.state_machine.current_state
        stability_score = float(stability_data.get("stability_score", 100.0))
        
        # 1. RUN MULTI-VARIATE CAUSAL CORRELATION CHECK
        correlation_report = self.correlation_engine.analyze_causal_chain(
            locomotion=locomotion_data, stability=stability_data, 
            mechanical=mechanical_data, thermal=thermal_data
        )

        # 2. DETERMINISTIC STATE MACHINE ROUTING (DHRUV CORE LOGIC)
        target_state = previous_state
        transition_reason = "Maintaining current frame metrics stability guidelines"

        if correlation_report["is_correlated_cascade"]:
            target_state = "EMERGENCY_STOP"
            transition_reason = "CORRELATED_PHYSICAL_FAILURE_CASCADE_DETECTED"
        elif stability_score < 50.0 and previous_state not in ["EMERGENCY_STOP", "SAFE_MODE"]:
            target_state = "UNSTABLE"
            transition_reason = "CRITICAL_STABILITY_DEGRADATION"

        if target_state != previous_state and previous_state != "EMERGENCY_STOP":
            self.state_machine.transit(target_state, transition_reason)

        current_state = self.state_machine.current_state
        severity = self.state_machine.determine_severity(current_state)

        # Bundle & Save Frame
        serialized_packet = self.synchronizer.bundle(
            locomotion_data=locomotion_data, mechanical_data=mechanical_data,
            stability_data=stability_data, thermal_data=thermal_data,
            trace_id=upstream_trace_id, current_state=current_state,
            previous_state=previous_state, transition_desc=transition_reason, severity=severity
        )

        with open(self.truth_file_path, "a", encoding="utf-8") as f:
            f.write(serialized_packet + "\n")

        # Paint Consolidated Live Dashboard Panel Screen
        os.system('cls' if os.name == 'nt' else 'clear')
        self._render_integrated_demo_dashboard(upstream_trace_id, current_state, previous_state, 
                                               transition_reason, severity, locomotion_data, 
                                               mechanical_data, stability_data, thermal_data, correlation_report)

    def _render_integrated_demo_dashboard(self, trace_id, current, previous, desc, severity, locomotion, mechanical, stability, thermal, report):
        # ARYA Data Extraction
        gait = locomotion.get("gait_phase", "STATIC_STANDBY")
        terrain = locomotion.get("terrain_type", "FLOWERBED_NOMINAL")
        
        # MANYA Data Extraction
        loads = mechanical.get("actuator_load", {"FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0})
        torques = mechanical.get("torque_requirements", {}).get("FL", {"knee": 0.0})
        stress_zones = mechanical.get("structural_stress_zones", ["NONE"])
        
        # Kinematics/Thermal Input
        score = stability.get("stability_score", 100.0)
        com = stability.get("com_position", [0.0, 0.0, 0.0])
        fl_sat = thermal.get("motor_saturation", {}).get("FL", {}).get("knee", 0.0) * 100

        print("=========================================================================")
        print("          TANTRA ROBOTICS INTEGRATED MULTI-NODE DEMO CONTROL             ")
        print("=========================================================================")
        print(f" [TRACE CONTEXT]  ID: {trace_id} | SEVERITY: {severity}")
        print(f" [DHRUV DIAGNOSTICS MACHINE] {previous} ──[{desc}]──> {current}")
        print("-------------------------------------------------------------------------")
        print(" [ARYA: LOCOMOTION NODE]")
        print(f"   Gait Phase   : {gait:<15} | Terrain Disturbance : {terrain}")
        print("-------------------------------------------------------------------------")
        print(" [MANYA: STRUCTURAL MECHANICS NODE]")
        print(f"   Actuator Loads: FL: {loads.get('FL',0.0):.2f} | FR: {loads.get('FR',0.0):.2f} | RL: {loads.get('RL',0.0):.2f} | RR: {loads.get('RR',0.0):.2f}")
        print(f"   FL Knee Torque: {torques.get('knee', 0.0):.1f} Nm      | Stress Zones Active : {', '.join(stress_zones)}")
        print("-------------------------------------------------------------------------")
        print(" [DHRUV: TELEMETRY ANALYSIS & VERDICT]")
        print(f"   Balance Score : {score:.1f} / 100.0     | CoM Coordinates     : X:{com[0]:.2f}, Y:{com[1]:.2f}")
        print(f"   Motor Saturation: {fl_sat:.1f}%          | Cascade Status      : {report['summary_verdict']}")
        print(" \n Evidence Timeline Trace Verification:")
        for log in report["evidence_chain"]:
            print(f"   => {log}")
        print("=========================================================================")