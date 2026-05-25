import os
import sys
import time
import json

# Path manipulation to expose workspace directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local system component imports
from Drivers.pipeline_sim import SimulatedRobot
from Layers.pipeline_sync import DataSynchronizer
from Core.fid import FailureIntelligence
from Telemetry.robot_control_interface import RobotControlInterface

def run_simulation_hook():
    # Instantiate pipeline blocks
    robot = SimulatedRobot()
    sync = DataSynchronizer()
    brain = FailureIntelligence()
    control = RobotControlInterface()
    
    print("--- PHASE 2 INTEGRATED TEST: NOMINAL TO GHOST_DIVE ---")
    
    # Iterate through target tracking profiles
    for mode in ["NOMINAL", "GHOST_DIVE"]:
        print(f"\n[HOOK] Setting Simulator to: {mode}")
        robot.set_simulation_mode(mode)
        
        for i in range(3):
            # 1. Sense: Gather raw stack dict from drivers
            raw_hw = robot.get_full_hardware_stack()
            
            # Generate expected pipeline contract fields
            upstream_trace_id = f"TANTRA-P5-MOCK-{int(time.time())}-{i}"
            mock_rajaryan_control = {"heartbeat": True, "command_sequence": i}
            
            # 2. Sync: Pass all 3 required contract fields to bundle()
            synced_json = sync.bundle(raw_hw, mock_rajaryan_control, upstream_trace_id)
            data = json.loads(synced_json)
            
            # 3. Think: Evaluate live runtime limits via the brain engine
            state, reason = brain.evaluate_system(data)
            
            # 4. Act: Translate states into joint profiles
            commands = control.process_decisions(state, data)
            
            # Parse tracking metrics
            trace = data.get('trace_id', upstream_trace_id)
            
            # Extract front left knee layout commands cleanly
            fl_t = commands['FRONT_LEFT']['THIGH']
            
            print(f"[{trace}] State: {state} | FL_Thigh: {fl_t:.2f} | LED: {commands['LED_STATUS']}")
            
            if state == "STOP":
                print(">> PHYSICAL TORQUE KILLED - SAFETY ENGAGED <<")
                
            time.sleep(0.1)

if __name__ == "__main__":
    run_simulation_hook()