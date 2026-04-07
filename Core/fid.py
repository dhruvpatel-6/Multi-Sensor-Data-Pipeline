import time

def process_failure_intelligence(sensors):
    """
    Intelligence Node: Upgraded from Detection to Actionable Response.
    Solves Task 3 Phase 4 requirements.
    """
    # Extraction: Safely getting values to avoid comparison errors
    depth_data = sensors.get('depth', {})
    distance = depth_data.get('dist', 0.0) 
    contact = depth_data.get('contact', False)
    
    # --- PHASE 4: RESPONSE-DRIVEN LOGIC ---
    
    # 1. CRITICAL: Imminent Collision (Response: STOP)
    if distance < 0.2:
        return "STOP", "IMMINENT_COLLISION"

    # 2. DEGRADED: Unstable Terrain (Response: Lower Speed)
    if distance > 0.3 and not contact:
        return "DEGRADED_MODE", "UNSTABLE_FOOTING"

    # 3. SAFE_MODE: Low Clearance (Response: Caution)
    if distance < 0.5:
        return "SAFE_MODE", "LOW_CLEARANCE"

    # 4. NOMINAL: Clear path
    return "NOMINAL", "NONE"