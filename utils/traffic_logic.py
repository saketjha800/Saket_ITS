def calculate_traffic_signal(vehicle_count, emergency_detected):
    """
    Traffic density aur emergency status ke hisaab se signal timing calculate karta hai.
    """
    if emergency_detected:
        return {
            "status": "GREEN (EMERGENCY OVERRIDE)",
            "timer": 0,
            "priority": "HIGH"
        }
    
    if vehicle_count == 0:
        timer = 10
    elif vehicle_count < 5:
        timer = 20
    elif vehicle_count < 15:
        timer = 35
    else:
        timer = 60
        
    return {
        "status": "NORMAL",
        "timer": timer,
        "priority": "NORMAL"
    }

def check_speed_and_chalan(speed, emergency_detected):
    """
    Agar speed 130 se zyada hai aur vehicle emergency nahi hai, toh chalan katega.
    """
    SPEED_LIMIT = 130
    
    if emergency_detected:
        return "EXEMPTED (Emergency Vehicle)", False
        
    if speed > SPEED_LIMIT:
        return f"CHALAN ISSUED! ({speed} km/h)", True
    else:
        return f"Normal ({speed} km/h)", False