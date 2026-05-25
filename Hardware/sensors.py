import random

def get_imu_data():
    # Phase 4: Added robustness for dropped packets
    if random.random() < 0.05: return None 
    return {"accel_z": round(random.uniform(-1, 1), 2)}

def get_depth_data():
    return {"dist": round(random.uniform(0.2, 4.0), 2)}

def get_contact_data():
    # Phase 2: Solving the 'Sensor Coverage' gap
    return random.choice(["GROUNDED", "IN_AIR"])