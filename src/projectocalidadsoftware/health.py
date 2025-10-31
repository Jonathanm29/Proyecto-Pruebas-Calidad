from src.projectocalidadsoftware.background import get_validation_status

def get_health_status():
    if get_validation_status():
        return {"colony_is_attacked": False}
    return {"colony_is_attacked": True}
