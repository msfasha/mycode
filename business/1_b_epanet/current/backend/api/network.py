"""Network management API endpoints."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from datetime import datetime
import uuid
import shutil

from config import NETWORKS_DIR
from services.network_loader import NetworkLoader
from services.baseline_engine import BaselineEngine
from models.network import NetworkInfo, Junction, Pipe, Tank, Reservoir, BaselineData
import database

router = APIRouter(prefix="/api/network", tags=["network"])

# In-memory storage (for quick access)
networks_storage: dict = {}
baselines_storage: dict = {}


@router.post("/upload")
async def upload_network(file: UploadFile = File(...)):
    """Upload an EPANET .inp file."""
    if not file.filename.endswith('.inp'):
        raise HTTPException(status_code=400, detail="File must be a .inp file")
    
    # Generate unique network ID
    network_id = str(uuid.uuid4())
    
    # Save file
    file_path = NETWORKS_DIR / f"{network_id}.inp"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Load and parse network
    try:
        loader = NetworkLoader(str(file_path))
        loader.load()
        network_info = loader.get_network_info()
        loader.close()
    except Exception as e:
        file_path.unlink()  # Delete file on error
        raise HTTPException(status_code=400, detail=f"Failed to load network: {str(e)}")
    
    # Store network info
    networks_storage[network_id] = {
        'network_id': network_id,
        'name': file.filename,
        'file_path': str(file_path),
        'created_at': datetime.now(),
        **network_info,
        'baseline_established': False
    }
    
    return {
        'network_id': network_id,
        'name': file.filename,
        'message': 'Network uploaded successfully'
    }


@router.get("/{network_id}")
async def get_network(network_id: str):
    """Get network information."""
    if network_id not in networks_storage:
        raise HTTPException(status_code=404, detail="Network not found")
    
    network_data = networks_storage[network_id]
    network_data['baseline_established'] = network_id in baselines_storage
    
    return NetworkInfo(**network_data)


@router.post("/{network_id}/baseline")
async def establish_baseline(network_id: str):
    """Establish baseline by running EPANET simulation."""
    if network_id not in networks_storage:
        raise HTTPException(status_code=404, detail="Network not found")
    
    network_data = networks_storage[network_id]
    file_path = network_data['file_path']
    
    try:
        engine = BaselineEngine(file_path)
        baseline = engine.establish_baseline()
        
        # Store baseline in memory
        baselines_storage[network_id] = baseline
        networks_storage[network_id]['baseline_established'] = True
        
        # Store in database (if available)
        try:
            await database.store_network(
                network_id,
                network_data['name'],
                file_path
            )
            await database.store_baseline(
                network_id,
                baseline['pressures'],
                baseline['flows'],
                baseline['tank_levels']
            )
        except Exception as db_error:
            print(f"Warning: Could not store in database: {db_error}")
            # Continue even if database fails
        
        return {
            'network_id': network_id,
            'message': 'Baseline established successfully',
            'baseline': BaselineData(network_id=network_id, **baseline)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to establish baseline: {str(e)}")


@router.get("/{network_id}/baseline")
async def get_baseline(network_id: str):
    """Get baseline data for a network."""
    if network_id not in networks_storage:
        raise HTTPException(status_code=404, detail="Network not found")
    
    if network_id not in baselines_storage:
        raise HTTPException(status_code=404, detail="Baseline not established")
    
    baseline = baselines_storage[network_id]
    return BaselineData(network_id=network_id, **baseline)

