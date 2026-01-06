from fastapi import FastAPI
from core import FractalTimeSystem
import time

app = FastAPI(title="Fractal 60 Calendar API")
system = FractalTimeSystem()

@app.get("/")
def read_root():
    return {"status": "active", "system": "13-Month / 60-Base Fractal Time"}

@app.get("/now")
def get_current_time():
    """Returns the current time in Fractal Format"""
    return system.timestamp_to_fractal(time.time())

@app.get("/convert/{timestamp}")
def convert_time(timestamp: float):
    """Converts any specific Unix timestamp"""
    return system.timestamp_to_fractal(timestamp)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
