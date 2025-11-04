# RTDWMS Backend

FastAPI backend for Real-Time Dynamic Water Network Monitoring System with SCADA simulator.

## Setup

1. Activate virtual environment:
```bash
source ../venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running

Start the server:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Network Management
- `POST /api/network/upload` - Upload .inp file
- `GET /api/network/{network_id}` - Get network info
- `POST /api/network/{network_id}/baseline` - Establish baseline
- `GET /api/network/{network_id}/baseline` - Get baseline data

### SCADA Data
- `GET /api/scada/{network_id}/sensors` - List all sensors
- `POST /api/scada/{network_id}/generate` - Generate SCADA data
- `GET /api/scada/{network_id}/data` - Get SCADA data for time range

## Usage Flow

1. Upload network file → Get `network_id`
2. Establish baseline → Run EPANET simulation
3. Generate SCADA data → Get sensor readings for time period



