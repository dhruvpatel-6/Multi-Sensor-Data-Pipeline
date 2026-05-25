def analyze_robot_state(imu, depth, contact):
    # Phase 3: Sensor Correlation (The 'Intelligence' part)
    if imu is None:
        return "DEGRADED", "IMU_PACKET_LOSS"
    
    # Logic: High acceleration while in the air is a fall
    if abs(imu['accel_z']) > 1.5 and contact == "IN_AIR":
        return "CRITICAL", "UNCONTROLLED_FALL"
    
    # Logic: Objects too close
    if depth['dist'] < 0.5:
        return "WARNING", "OBSTACLE_NEAR"
        
    return "HEALTHY", "NOMINAL"

import time

class DataIntegrityProtection:
    def __init__(self):
        self.last_valid_imu = {'accel_z': 1.0} # Default gravity
        self.last_valid_depth = 0.0

    def validate_packet(self, data_packet):
        """
        DIP Logic: Fills the gaps for missing/empty datasets.
        """
        # 1. CHECK FOR EMPTY DATASETS
        if not data_packet or len(data_packet) == 0:
            return False, "CRITICAL: Empty Dataset Received"

        # 2. FILL GAPS: MISSING IMU DATA
        if 'imu' not in data_packet or data_packet['imu'] is None:
            # DIP Action: Inject last known good value to prevent crash
            data_packet['imu'] = self.last_valid_imu
            print("DIP: Missing IMU data filled with last valid state.")
        else:
            self.last_valid_imu = data_packet['imu']

        # 3. FILL GAPS: MISSING DEPTH DATA
        if 'depth' not in data_packet or data_packet['depth'] is None:
            # DIP Action: Mark as 'Unknown' so FID can handle the caution
            data_packet['depth'] = {'dist': -1.0} 
            print("DIP: Missing Depth data flagged as -1.")
        
        # 4. DATA INTEGRITY: SENSITIVITY CHECK (DIP Shield)
        # Check if the keys exist but values are 'NaN' or 'None'
        for key, value in data_packet.items():
            if value is None:
                return False, f"DIP: Corrupted field detected in {key}"

        return True, data_packet

# --- HOW TO INTEGRATE INTO YOUR MAIN TELEMETRY ---
# dip = DataIntegrityProtection()
# is_valid, cleaned_data = dip.validate_packet(raw_data)
# if is_valid:
#     # Pass 'cleaned_data' to your FID.py for analysis