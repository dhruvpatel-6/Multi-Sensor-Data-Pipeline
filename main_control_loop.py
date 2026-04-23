# main_control_loop.py - Phase 4: 10Hz Integrated Loop
import time
from Drivers.pipeline_sim import SimulatedRobot  # Assuming your sim class
from Layers.pipeline_sync import DataSynchronizer
from Core.fid import FailureIntelligence
from robot_control_interface import RobotControlInterface

def start_robot_mission():
    # Initialize all subsystems
    robot_hardware = SimulatedRobot()
    sync_layer = DataSynchronizer()
    brain = FailureIntelligence()
    spinal_cord = RobotControlInterface()
    
    print("--- QUADRUPED CONTROL LOOP STARTING (10Hz) ---")

    try:
        while True:
            start_time = time.time()

            # 1. FETCH & SYNC (Sense)
            raw_data = robot_hardware.get_telemetry()
            synced_packet = sync_layer.bundle(raw_data)

            # 2. EVALUATE (Think)
            # We calculate latency to pass to FID
            loop_latency = time.time() - start_time
            current_state = brain.evaluate_system(synced_packet, loop_latency)

            # 3. ACTUATE (Act)
            # Convert decision into motor commands
            motor_commands = spinal_cord.process_decisions(current_state, synced_packet)

            # 4. MONITOR (Output)
            print(f"State: {current_state} | Motors: {motor_commands['FL_MOTOR']:.2f} | LED: {motor_commands['LED_STATUS']}")

            # 5. TIMING CONTROL (The 10Hz Metronome)
            elapsed = time.time() - start_time
            sleep_time = max(0, 0.1 - elapsed) # Maintain 100ms cycle
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[SYSTEM] Manual Shutdown Received. Stopping Robot Safely...")
        spinal_cord._emergency_shutdown()

if __name__ == "__main__":
    start_robot_mission()