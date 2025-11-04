# Monitoring Engine Implementation with Extended Period Simulation

## Overview

This document describes the implementation of the monitoring and anomaly detection system that uses **EPANET Extended Period Simulation (EPS)** step-by-step to compare expected values from hydraulic analysis with actual SCADA sensor readings.

## Implementation Approach

### Selected Approach: Extended Period Simulation (EPS) Step-by-Step

We implemented **Extended Period Simulation** using incremental step-by-step advancement rather than point-in-time snapshots. This ensures:

1. **Correct Tank Level Tracking**: Tank levels change cumulatively over time based on inflows/outflows. EPS maintains this state automatically.
2. **Efficiency**: Only advances one time step per monitoring interval (no full re-simulation from start).
3. **Network State Continuity**: All system state (pressures, flows, tank levels) is preserved between steps.
4. **Accuracy**: Accounts for network interactions and cumulative effects.

## Architecture

### Components

1. **MonitoringEngine** (`backend/services/monitoring_engine.py`)
   - Manages EPANET Extended Period Simulation
   - Advances simulation step-by-step using `nextHydraulicAnalysisStep()`
   - Extracts expected values at each time step
   - Compares expected vs actual and detects anomalies

2. **SimulationRunner** (`backend/services/simulation_runner.py`)
   - Integrates monitoring into simulation loop
   - Coordinates: EPS step → SCADA generation → Comparison → Storage
   - Manages lifecycle of monitoring engines

3. **Database** (`backend/database.py`)
   - Stores SCADA readings
   - Stores detected anomalies
   - Provides queries for anomaly history

4. **API Endpoints** (`backend/api/simulation.py`)
   - Start/stop simulation with monitoring
   - Get anomaly reports
   - Configurable monitoring intervals

## Workflow

### 1. Initialization Phase

```
1. Load EPANET network file (.inp)
2. Create 24-hour diurnal pattern:
   - Pattern[0-23]: multipliers for each hour of day
   - Values range from 0.6 (low demand) to 1.4 (peak demand)
3. Assign pattern to all junction demands
4. Set EPS parameters:
   - Duration: 24 hours
   - Hydraulic step: 1 minute
   - Pattern step: 1 hour
5. Initialize hydraulic analysis (starts at t=0)
```

### 2. Monitoring Loop (Every N Minutes)

```
At each monitoring interval (default: 5 minutes):

Step 1: Advance EPANET EPS
  ├─ Call nextHydraulicAnalysisStep()
  ├─ EPANET advances one time step
  ├─ Tank levels updated based on cumulative inflows/outflows
  └─ System state preserved

Step 2: Extract Expected Values
  ├─ Get pressures at all junctions/tanks
  ├─ Get flows in all pipes
  └─ Get tank levels (cumulative, from EPS)

Step 3: Generate Actual SCADA Readings
  ├─ Use SCADASimulator to generate sensor data
  ├─ Apply time-of-day patterns + noise
  └─ Generate readings for all sensors

Step 4: Update Tank Levels from SCADA (Optional)
  ├─ Use actual tank level readings from SCADA
  ├─ Update EPANET tank initial conditions
  └─ Improves prediction accuracy

Step 5: Compare and Detect Anomalies
  ├─ For each sensor reading:
  │   ├─ Calculate: deviation = |actual - expected| / expected × 100
  │   ├─ Compare with threshold:
  │   │   ├─ Pressure: 10% threshold
  │   │   ├─ Flow: 15% threshold
  │   │   └─ Level: 5% threshold
  │   └─ If deviation > threshold → Flag as anomaly
  └─ Classify severity:
      ├─ Medium: 1.0x - 1.5x threshold
      ├─ High: 1.5x - 2.0x threshold
      └─ Critical: > 2.0x threshold

Step 6: Store Results
  ├─ Store SCADA readings in database
  └─ Store anomalies in database

Step 7: Wait for Next Interval
  └─ Sleep for interval_minutes × 60 seconds
```

### 3. Pattern Definition

24-hour diurnal pattern generated from `time_patterns.py`:

```python
# Example pattern values:
Hour 0-5:   0.7-0.8  (Night low)
Hour 6-7:   0.7-1.4  (Morning rise)
Hour 8-9:   1.4       (Morning peak)
Hour 10-11: 1.2-1.4   (Post-morning)
Hour 12-13: 0.8-1.0   (Midday)
Hour 14-17: 0.6-0.9   (Afternoon)
Hour 18-19: 0.9-1.3   (Evening peak)
Hour 20-23: 0.8-1.0   (Evening to night)
```

## Key Features

### 1. Extended Period Simulation

- **Initialization**: EPANET object kept open throughout monitoring session
- **Step-by-Step Advancement**: Uses `nextHydraulicAnalysisStep()` to advance one time step
- **Auto-Restart**: When 24 hours reached, simulation restarts from beginning
- **State Preservation**: Tank levels, pressures, flows maintained between steps

### 2. Tank Level Tracking

**Problem**: Tank levels change cumulatively over time. Simple snapshot simulation doesn't account for this.

**Solution**: 
- EPS automatically tracks tank levels based on inflows/outflows
- Optionally updates from actual SCADA readings for accuracy
- Maintains correct system state throughout the day

### 3. Anomaly Detection

**Thresholds**:
- Pressure: 10% deviation
- Flow: 15% deviation  
- Tank Level: 5% deviation

**Severity Classification**:
- **Medium**: 1.0x - 1.5x threshold (e.g., 10-15% for pressure)
- **High**: 1.5x - 2.0x threshold (e.g., 15-20% for pressure)
- **Critical**: > 2.0x threshold (e.g., > 20% for pressure)

### 4. Configurable Monitoring Interval

Default: 5 minutes. Can be configured to:
- 1 minute (high frequency)
- 5 minutes (default)
- 10, 15, 20, 30, 60 minutes (lower frequency)

## Database Schema

### SCADA Readings Table
```sql
scada_readings (
    id BIGSERIAL PRIMARY KEY,
    network_id UUID,
    timestamp TIMESTAMPTZ,
    sensor_id TEXT,
    sensor_type TEXT,
    value REAL,
    location_id TEXT
)
```

### Anomalies Table
```sql
anomalies (
    id BIGSERIAL PRIMARY KEY,
    network_id UUID,
    timestamp TIMESTAMPTZ,
    sensor_id TEXT,
    sensor_type TEXT,
    location_id TEXT,
    actual_value REAL,
    expected_value REAL,
    deviation_percent REAL,
    threshold REAL,
    severity TEXT  -- 'medium', 'high', 'critical'
)
```

## API Endpoints

### Start Simulation with Monitoring
```
POST /api/simulation/start
{
    "network_id": "uuid",
    "interval_minutes": 5  // Optional, default: 5
}

Response:
{
    "success": true,
    "network_id": "uuid",
    "interval_minutes": 5,
    "message": "Simulation started with monitoring..."
}
```

### Stop Simulation
```
POST /api/simulation/stop
{
    "network_id": "uuid"
}
```

### Get Anomalies
```
GET /api/simulation/anomalies/{network_id}?severity=high&limit=100

Response:
{
    "network_id": "uuid",
    "count": 15,
    "anomalies": [
        {
            "id": 123,
            "timestamp": "2024-10-29T08:30:00",
            "sensor_id": "PRESSURE_29",
            "sensor_type": "pressure",
            "location_id": "29",
            "actual_value": 38.5,
            "expected_value": 45.2,
            "deviation_percent": 14.82,
            "threshold": 10.0,
            "severity": "high"
        },
        ...
    ]
}
```

## Implementation Files

### Core Services
- `backend/services/monitoring_engine.py` - EPS-based monitoring engine
- `backend/services/simulation_runner.py` - Integrated simulation + monitoring loop
- `backend/services/scada_simulator.py` - SCADA data generation
- `backend/services/baseline_engine.py` - Baseline establishment (updated to extract demands)
- `backend/services/time_patterns.py` - 24-hour diurnal patterns

### Database
- `backend/database.py` - Database operations, anomaly storage

### API
- `backend/api/simulation.py` - Simulation and anomaly endpoints

## Advantages of EPS Step-by-Step Approach

1. **Correct Physics**: Tank levels tracked correctly through cumulative simulation
2. **Efficient**: Only one step calculation, not full re-simulation
3. **Accurate**: Network state maintained between steps
4. **Scalable**: Works for long-running monitoring sessions
5. **Maintainable**: EPANET handles state internally

## Future Enhancements

1. **Anomaly Injection**: Option to inject simulated anomalies for testing
2. **Real Sensor Integration**: Replace SCADA simulator with real sensor API
3. **Alert System**: Email/SMS notifications for critical anomalies
4. **Anomaly Dashboard**: Frontend visualization of detected anomalies
5. **Machine Learning**: Advanced anomaly detection using ML models
6. **Historical Analysis**: Trend analysis and pattern recognition

## Testing

The system has been tested with:
- Network file: `yasmin.inp` (Amman city network)
- Monitoring intervals: 1, 5, 10 minutes
- Anomaly detection: Verified with various deviation thresholds
- Database storage: Confirmed SCADA readings and anomalies are stored

## Status

✅ **Implemented and Functional**
- Extended Period Simulation step-by-step
- Anomaly detection with configurable thresholds
- Database storage for SCADA and anomalies
- API endpoints for simulation and anomaly retrieval
- Configurable monitoring intervals

