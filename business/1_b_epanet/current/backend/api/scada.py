"""SCADA data API endpoints."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List

from api.network import baselines_storage, networks_storage
from services.scada_simulator import SCADASimulator
from models.scada import SensorData, SCADADataRequest, SensorInfo

router = APIRouter(prefix="/api/scada", tags=["scada"])


@router.get("/{network_id}/sensors")
async def list_sensors(network_id: str):
    """List all available sensors for a network."""
    if network_id not in networks_storage:
        raise HTTPException(status_code=404, detail="Network not found")
    
    if network_id not in baselines_storage:
        raise HTTPException(status_code=404, detail="Baseline not established. Please establish baseline first.")
    
    baseline = baselines_storage[network_id]
    simulator = SCADASimulator(baseline)
    sensors = simulator.get_sensor_list()
    
    return [SensorInfo(**sensor) for sensor in sensors]


@router.post("/{network_id}/generate")
async def generate_scada_data(network_id: str, request: SCADADataRequest):
    """Generate SCADA data for a time period."""
    if network_id != request.network_id:
        raise HTTPException(status_code=400, detail="Network ID mismatch")
    
    if network_id not in networks_storage:
        raise HTTPException(status_code=404, detail="Network not found")
    
    if network_id not in baselines_storage:
        raise HTTPException(status_code=404, detail="Baseline not established. Please establish baseline first.")
    
    if request.start_time >= request.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")
    
    try:
        baseline = baselines_storage[network_id]
        simulator = SCADASimulator(baseline)
        sensor_data = simulator.generate_sensor_data(
            request.start_time,
            request.end_time,
            request.interval_minutes
        )
        
        return [SensorData(**reading) for reading in sensor_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SCADA data: {str(e)}")


@router.get("/{network_id}/data")
async def get_scada_data(
    network_id: str,
    start_time: datetime,
    end_time: datetime,
    interval_minutes: int = 1
):
    """Get SCADA data for a time period (convenience endpoint)."""
    request = SCADADataRequest(
        network_id=network_id,
        start_time=start_time,
        end_time=end_time,
        interval_minutes=interval_minutes
    )
    return await generate_scada_data(network_id, request)

