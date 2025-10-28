from src.projectocalidadsoftware.background import get_validation_status

def get_health_status():
    if get_validation_status():
        return "OK"
    return "ERROR"
