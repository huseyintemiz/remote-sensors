"""FastAPI server for receiving and displaying sensor data."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any
from database import data_store

app = FastAPI(title="Remote Sensor Monitor", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class SensorReading(BaseModel):
    """Model for incoming sensor data."""
    hostname: str
    os: str
    timestamp: float
    cpu_temp: Optional[float] = None
    gpu_temp: Optional[float] = None
    memory_usage: Optional[Dict[str, Any]] = None


@app.post("/ingest")
async def ingest_data(reading: SensorReading):
    """
    Receive sensor data from agents.

    Args:
        reading: Sensor reading data

    Returns:
        Status response
    """
    data_store.add_reading(reading.dict())
    return {"status": "ok", "hostname": reading.hostname}


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Render main dashboard page.

    Args:
        request: FastAPI request object

    Returns:
        HTML response with dashboard
    """
    machines = data_store.get_current_data()

    # Format timestamps for display
    for hostname, data in machines.items():
        data["formatted_time"] = data_store.format_timestamp(data["timestamp"])

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "machines": machines}
    )


@app.get("/api/current")
async def get_current_data():
    """
    Get current sensor readings for all machines (JSON API).

    Returns:
        JSON response with current data
    """
    return JSONResponse(content=data_store.get_current_data())


@app.get("/api/history/{hostname}")
async def get_history(hostname: str, limit: int = 60):
    """
    Get historical data for a specific machine (JSON API).

    Args:
        hostname: Machine hostname
        limit: Maximum number of readings to return

    Returns:
        JSON response with historical data
    """
    history = data_store.get_history(hostname, limit)
    return JSONResponse(content={"hostname": hostname, "readings": history})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "machines_count": len(data_store.get_all_hostnames())
    }
