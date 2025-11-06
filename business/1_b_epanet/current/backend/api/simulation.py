"""Simulation management API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.network import baselines_storage, networks_storage
from services.simulation_runner import simulation_runner
import database

router = APIRouter(prefix="/api/simulation", tags=["simulation"])


class StartSimulationRequest(BaseModel):
    """Request to start simulation."""
    network_id: str
    interval_minutes: Optional[int] = 5  # Monitoring interval in minutes


class StopSimulationRequest(BaseModel):
    """Request to stop simulation."""
    network_id: str


@router.post("/start")
async def start_simulation(request: StartSimulationRequest):
    """Start continuous simulation for a network."""
    network_id = request.network_id
    
    if network_id not in networks_storage:
        raise HTTPException(status_code=404, detail="Network not found")
    
    if network_id not in baselines_storage:
        raise HTTPException(status_code=404, detail="Baseline not established")
    
    # Check database connection (non-fatal, simulation can run without it)
    db_available = await database.check_connection()
    db_warning = None
    if not db_available:
        db_warning = "Database is not available. Simulation will run but data will not be stored."
    
    # Try to store network in database (non-fatal)
    network_data = networks_storage[network_id]
    try:
        await database.store_network(
            network_id,
            network_data['name'],
            network_data['file_path']
        )
    except Exception as db_error:
        db_warning = f"Database storage failed: {db_error}. Simulation will continue without database."
    
    # Try to store baseline in database (non-fatal)
    baseline = baselines_storage[network_id]
    try:
        await database.store_baseline(
            network_id,
            baseline['pressures'],
            baseline['flows'],
            baseline['tank_levels']
        )
    except Exception as db_error:
        if not db_warning:
            db_warning = f"Database storage failed: {db_error}. Simulation will continue without database."
    
    # Get network file path
    network_file = network_data['file_path']
    interval_minutes = request.interval_minutes or 5
    
    # Clear any previous errors for this simulation
    simulation_runner.clear_errors(network_id)
    
    # Start simulation with monitoring
    try:
        success = await simulation_runner.start_simulation(
            network_id, 
            baseline, 
            network_file,
            interval_minutes=interval_minutes
        )
    except Exception as init_error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start simulation: {str(init_error)}"
        )
    
    if not success:
        raise HTTPException(status_code=400, detail="Simulation already running")
    
    response = {
        "success": True,
        "network_id": network_id,
        "interval_minutes": interval_minutes,
        "message": f"Simulation started with monitoring. Comparing expected vs actual every {interval_minutes} minutes."
    }
    
    if db_warning:
        response["warning"] = db_warning
    
    return response


@router.post("/stop")
async def stop_simulation(request: StopSimulationRequest):
    """Stop simulation for a network."""
    network_id = request.network_id
    
    success = await simulation_runner.stop_simulation(network_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Simulation not running")
    
    return {
        "success": True,
        "network_id": network_id,
        "message": "Simulation stopped"
    }


@router.get("/status/{network_id}")
async def get_simulation_status(network_id: str):
    """Get simulation status for a network."""
    is_running = simulation_runner.is_running(network_id)
    errors = simulation_runner.get_errors(network_id)
    
    # Get recent errors (last 10)
    recent_errors = errors[-10:] if errors else []
    
    # Count errors by type
    fatal_count = sum(1 for e in errors if e.get('fatal', False))
    recoverable_count = sum(1 for e in errors if not e.get('fatal', False))
    
    return {
        "network_id": network_id,
        "running": is_running,
        "errors": {
            "total": len(errors),
            "fatal": fatal_count,
            "recoverable": recoverable_count,
            "recent": recent_errors
        }
    }


@router.get("/errors/{network_id}")
async def get_simulation_errors(
    network_id: str,
    limit: int = 50,
    fatal_only: bool = False
):
    """Get errors for a simulation."""
    if network_id not in networks_storage:
        raise HTTPException(status_code=404, detail="Network not found")
    
    errors = simulation_runner.get_errors(network_id)
    
    # Filter by fatal if requested
    if fatal_only:
        errors = [e for e in errors if e.get('fatal', False)]
    
    # Limit results
    errors = errors[-limit:] if len(errors) > limit else errors
    
    return {
        "network_id": network_id,
        "count": len(errors),
        "errors": errors
    }


@router.get("/anomalies/{network_id}")
async def get_anomalies(
    network_id: str,
    severity: Optional[str] = None,
    limit: int = 100
):
    """Get detected anomalies for a network."""
    if network_id not in networks_storage:
        raise HTTPException(status_code=404, detail="Network not found")
    
    from datetime import datetime, timedelta
    
    # Default: last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    anomalies = await database.get_anomalies(
        network_id,
        start_time=start_time,
        end_time=end_time,
        severity=severity
    )
    
    # Limit results
    anomalies = anomalies[:limit]
    
    return {
        "network_id": network_id,
        "count": len(anomalies),
        "anomalies": anomalies
    }


