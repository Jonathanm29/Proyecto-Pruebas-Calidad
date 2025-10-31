from fastapi import FastAPI
import threading

from src.projectocalidadsoftware.background import start_background_loop
from src.projectocalidadsoftware.health import get_health_status

app = FastAPI(title="Defense System")
threading.Thread(target=start_background_loop, daemon=True).start()

@app.get("/health/status")
def health_status():
    return get_health_status()
