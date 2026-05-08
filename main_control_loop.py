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

    # robot_control_interface.py - Closed-Loop sustained correction

class RobotControlInterface:
    def __init__(self):
        self.MAX_TORQUE = 12.0
        self.KP = 0.15  # Proportional Gain: How "hard" the robot fights back
        self.TARGET_PITCH = 0.0
        self.commands = self._get_empty_map()

    def _calculate_balance(self, telemetry):
        """
        SUSTAINED CLOSED-LOOP CORRECTION
        This runs every cycle (10Hz) to 'steer' the robot back to level.
        """
        current_pitch = telemetry.get('pitch', 0)
        
        # 1. Calculate Error
        error = current_pitch - self.TARGET_PITCH
        
        # 2. Proportional Correction
        # Torque scales dynamically with the severity of the tilt
        sustained_torque = error * self.KP
        
        # 3. Apply to 12-DOF Mapping
        # As 'error' approaches 0, torque automatically fades away
        for leg in ["FRONT_LEFT", "FRONT_RIGHT"]:
            self.commands[leg]["THIGH"] = sustained_torque
            self.commands[leg]["CALF"] = sustained_torque * 0.4
            
        if abs(error) > 1.0:
            print(f"[LOOP] Error: {error:.2f}° | Applying Sustained Torque: {sustained_torque:.2f}Nm")

    def _enforce_physical_limits(self):
        # (Same as previous: clips torque to MAX_TORQUE)
        for leg in ["FRONT_LEFT", "FRONT_RIGHT", "REAR_LEFT", "REAR_RIGHT"]:
            for joint in ["HIP", "THIGH", "CALF"]:
                self.commands[leg][joint] = max(-self.MAX_TORQUE, min(self.MAX_TORQUE, self.commands[leg][joint]))