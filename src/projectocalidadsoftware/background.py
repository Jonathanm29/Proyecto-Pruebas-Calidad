import time

_last_validation_ok = True

# TODO: Usar este metodo para anadir la logica para defender la colonia
def defend_colony():
    global _last_validation_ok
    print("Checking for attacks to the colony...")
    _last_validation_ok = True

def start_background_loop():
    while True:
        defend_colony()
        time.sleep(10)

def get_validation_status():
    return _last_validation_ok
