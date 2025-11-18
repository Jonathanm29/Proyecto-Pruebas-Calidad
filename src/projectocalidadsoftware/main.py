from fastapi import FastAPI
import threading

from src.projectocalidadsoftware.health import get_health_status

app = FastAPI(title="Defense System")

@app.get("/health/status")
def health_status():
    return get_health_status()
