# main_control_loop.py - Phase 4: 10Hz Integrated Loop
import time
from Drivers.pipeline_sim import SimulatedRobot
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
            loop_latency = time.time() - start_time
            current_state = brain.evaluate_system(synced_packet, loop_latency)

            # 3. ACTUATE (Act)
            # motor_commands now contains the 12-DOF nested dictionary
            motor_commands = spinal_cord.process_decisions(current_state, synced_packet)

            # 4. MONITOR (Output) - Updated for 12-DOF Clarity
            led = motor_commands['LED_STATUS']
            
            # We display the Front Left leg joints as a representative sample in the main log
            fl_t = motor_commands['FRONT_LEFT']['THIGH']
            fl_c = motor_commands['FRONT_LEFT']['CALF']
            
            print(f"State: {current_state} | FL_Thigh: {fl_t:.2f} | FL_Calf: {fl_c:.2f} | LED: {led}")

            # 5. TIMING CONTROL (The 10Hz Metronome)
            elapsed = time.time() - start_time
            sleep_time = max(0, 0.1 - elapsed) # Maintain 100ms cycle
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[SYSTEM] Manual Shutdown Received. Stopping Robot Safely...")
        spinal_cord._emergency_shutdown()

if __name__ == "__main__":
    start_robot_mission()