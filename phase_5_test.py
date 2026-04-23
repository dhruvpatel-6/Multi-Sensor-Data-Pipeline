import time
from Drivers.pipeline_sim import SimulatedRobot
from Layers.pipeline_sync import DataSynchronizer
from Core.fid import FailureIntelligence
from robot_control_interface import RobotControlInterface

def run_simulation_hook():
    print("--- STARTING PHASE 5: SIMULATION HOOK TEST ---")
    
    # Initialize the components
    robot = SimulatedRobot()
    sync = DataSynchronizer()
    brain = FailureIntelligence()
    control = RobotControlInterface()

    # Step 1: Nominal Mode
    print("\n[HOOK] System running in NOMINAL mode...")
    robot.set_simulation_mode("NOMINAL")
    
    for _ in range(3):
        data = robot.get_telemetry()
        # Ensure we pass latency (0.05s) to evaluate_system
        state = brain.evaluate_system(data, 0.05)
        commands = control.process_decisions(state, data)
        print(f"State: {state} | FL_Motor: {commands['FL_MOTOR']} | LED: {commands['LED_STATUS']}")
        time.sleep(0.1)

    # Step 2: Trigger the Hook (The "Virtual Kick")
    print("\n[HOOK] TRIGGERING 'GHOST_DIVE'...")
    robot.set_simulation_mode("GHOST_DIVE")
    
    # Step 3: Show the reaction!
    for _ in range(5):
        data = robot.get_telemetry()
        state = brain.evaluate_system(data, 0.05)
        commands = control.process_decisions(state, data)
        print(f"State: {state} | FL_Motor: {commands['FL_MOTOR']} | LED: {commands['LED_STATUS']}")
        time.sleep(0.1)

if __name__ == "__main__":
    run_simulation_hook()