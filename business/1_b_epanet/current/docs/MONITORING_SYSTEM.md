# Water Network Monitoring System

## Overview

The monitoring system continuously monitors a **real water distribution network** by comparing **expected values** (from EPANET hydraulic analysis) with **actual values** (from SCADA sensors) to detect anomalies in real-time.

## What's Real vs Simulated

**Real Components:**
- **Water Network**: Real network topology, pipes, junctions, tanks (from .inp file)
- **EPANET Hydraulic Analysis**: Real hydraulic calculations predicting network behavior
- **Expected Values**: Real predictions based on actual network physics

**Simulated Component (Temporary):**
- **SCADA Sensor Readings**: Currently simulated because real sensors aren't connected yet
  - When real SCADA sensors are available, simply replace the simulator with real sensor data
  - The simulator generates realistic readings based on baseline + patterns + noise

**Note**: This is a **monitoring system**, not a simulation system. The network analysis is real. Only the sensor data is simulated temporarily.

## Core Concept

The system works on a simple principle:
1. **EPANET** predicts what the network values *should* be (pressures, flows, tank levels)
2. **SCADA sensors** report what the values *actually* are
3. **Comparison** detects when actual deviates significantly from expected → **Anomaly**

## System Architecture

### Components

```
┌─────────────────┐
│  Frontend       │  User controls:
│  (React)        │  - Start/Stop SCADA Simulator
│                 │  - Start/Stop Monitoring
│                 │  - Configure: generation rate, data loss %, delay params
│                 │  - View real-time status of both processes
└────────┬────────┘
         │
         │ (queries status)
         │
         ▼
┌─────────────────┐
│  Backend API    │  Receives control requests
│  (FastAPI)      │  Provides status endpoints
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────────────┐  ┌─────────────────┐
│ SCADA           │  │ Monitoring      │
│ Simulator       │  │ Service         │
│ (Autonomous)    │  │                 │
│                 │  │                 │
│ - Runs          │  │ - Queries DB    │
│   independently │  │   for readings  │
│ - Generates     │  │ - Gets expected │
│   readings at   │  │   from EPANET   │
│   configurable  │  │ - Compares &    │
│   intervals     │  │   detects       │
│ - Simulates     │  │   anomalies     │
│   data loss     │  │                 │
│ - Applies       │  │                 │
│   timestamp     │  │                 │
│   delays        │  │                 │
│ - Maintains     │  │ - Maintains     │
│   status        │  │   status        │
└────────┬────────┘  └────────┬────────┘
         │                    │
         │                    │
         └──────────┬─────────┘
                    │
                    ▼
         ┌─────────────────┐
         │ Database        │  Store readings & anomalies
         │ (PostgreSQL)    │  Store process status
         └─────────────────┘
                    │
                    ▼
         ┌─────────────────┐
         │ Monitoring      │  EPANET Extended Period
         │ Engine (EPANET) │  Simulation
         └─────────────────┘
```

## How It Works: Step-by-Step

### Phase 1: Network Setup

1. **Network Upload**
   - Network file (.inp) is uploaded to backend
   - Stored in `networks/` directory
   - Network ID generated

2. **Baseline Establishment**
   - EPANET runs a complete hydraulic simulation
   - Extracts "normal" values:
     - Pressures at all junctions and tanks
     - Flows in all pipes
     - Tank levels
     - Demands at junctions
   - These become the **baseline** (reference point)

### Phase 2: SCADA Simulator (Autonomous Process)

The SCADA simulator runs as an **independent, autonomous process** that can be started and stopped from the frontend.

#### Starting the SCADA Simulator

When you click "Start SCADA Simulator" in the frontend:

1. **Configuration** (set in frontend):
   - **Generation Rate**: How often to generate readings (1, 2, 3, 15, 60 minutes, etc.)
   - **Data Loss Proportion**: Percentage of network items to include (e.g., 90% = 10% data loss)
   - **Delay Configuration**:
     - **Delay Mean**: Mean delay for truncated normal distribution (default: 2.5 minutes)
     - **Delay Standard Deviation**: Standard deviation for delays (default: 2.0 minutes)
     - **Maximum Delay**: Upper bound for delays (default: 10 minutes)
     - Delays are bounded between 0 and maximum delay
     - Delays are always positive (readings arrive late, never early)
     - No reading can have a future timestamp

2. **Simulator Initialization**:
   - Loads network information (junctions, pipes, tanks)
   - Initialized with baseline data
   - Creates 24-hour diurnal demand pattern
   - Sets status to "starting"
   - Starts autonomous generation loop
   - Updates status to "running" when loop begins

#### SCADA Generation Loop (Runs Continuously)

The simulator runs independently at the configured generation rate:

```
Every N minutes (configurable: 1, 2, 3, 15, 60, etc.):

1. Get Current Real-Time
   - Current time: e.g., 2:05 PM
   - Current hour: 14 (for pattern lookup)

2. Randomly Select Network Items (Data Loss Simulation)
   - Randomly select X% of junctions (e.g., 90% of 150 = 135 junctions)
   - Randomly select X% of pipes (e.g., 90% of 200 = 180 pipes)
   - Randomly select X% of tanks (e.g., 90% of 5 = 4-5 tanks)
   - Selection is re-randomized each cycle (simulates intermittent failures)

3. Generate Readings for Selected Items
   For each selected sensor:
   - Calculate value: baseline × pattern_multiplier × noise
   - Pattern multiplier based on current hour (diurnal pattern)
   - Add realistic noise (±2% pressure, ±3% flow, ±1% level)
   
4. Apply Timestamp Delays
   For each reading:
   - Generation time: current real-time (e.g., 2:05 PM)
   - Delay: sample from bounded distribution (0 to max_delay minutes)
     - **Recommended**: Truncated normal distribution
       - Mean: configurable (default: 2.5 min)
       - Standard deviation: configurable (default: 2.0 min)
       - Bounds: [0, max_delay] where max_delay is configurable (default: 10 min)
     - **Alternative**: Exponential distribution
       - Scale parameter: configurable (default: 2.5 min)
       - Bounded to [0, max_delay]
     - Ensures delays are bounded and realistic
     - Ensures no reading has a future timestamp
   - Reading timestamp: generation_time - delay (reading arrives late)
   - Example: Generated at 2:05 PM, delay = 3.2 min → timestamp = 2:01:48 PM
   - Example: Generated at 2:05 PM, delay = 0.5 min → timestamp = 2:04:30 PM
   - **Important**: All readings have timestamps in the past (simulates transmission/processing delays)

5. Store Readings in Database
   - All generated readings stored with their delayed timestamps
   - Includes: timestamp, sensor_id, sensor_type, value, location_id, network_id

6. Update Status
   - Updates status with:
     - Last generation time
     - Total readings generated
     - Current configuration (rate, data loss %, delay params)
     - Status: "running"
```

**Key Points**:
- Simulator runs **independently** of monitoring service
- Generation rate is **configurable** from frontend
- Data loss is **simulated** by randomly selecting a proportion each cycle
- Timestamps have **bounded one-directional delays** (0 to max_delay minutes)
  - Uses truncated normal distribution (bounded, realistic)
  - No reading can have a future timestamp
  - Simulates realistic transmission/processing delays
- Readings are stored **asynchronously** as they're generated
- Status is **continuously updated** and accessible from frontend

**Stopping the SCADA Simulator**:
- When you click "Stop SCADA Simulator" in the frontend:
  - Simulator gracefully stops the generation loop
  - Updates status to "stopped"
  - Status remains queryable from frontend

### Phase 3: Monitoring Service (Separate Process)

The monitoring service runs as a **separate process** that can be started and stopped independently from the SCADA simulator.

#### Starting the Monitoring Service

When you click "Start Monitoring" in the frontend:

1. **Monitoring Engine Setup**:
   - Loads EPANET network file
   - Creates 24-hour diurnal demand pattern
   - Assigns pattern to all junctions
   - Initializes Extended Period Simulation (EPS)
   - **Catches up to real-time**: If you start at 2:00 PM, EPS advances 14 hours to sync

2. **Monitoring Loop Begins**:
   - Sets status to "starting"
   - Runs at configurable intervals (default: 5 minutes)
   - Queries database for recent SCADA readings
   - Compares with EPANET expected values
   - Detects anomalies
   - Updates status to "running" when loop begins

**Stopping the Monitoring Service**:
- When you click "Stop Monitoring" in the frontend:
  - Monitoring service gracefully stops the monitoring loop
  - Updates status to "stopped"
  - Status remains queryable from frontend

### Phase 2: Continuous Monitoring Loop

The monitoring loop runs every **5 minutes** (configurable):

#### Step 1: Get Expected Values from EPANET

```
Current Time: 2:05 PM (real-world)
Elapsed since start: 5 minutes
EPS Time: 14:05 (synchronized to real-time)

EPANET calculates:
- Expected pressures at each junction/tank
- Expected flows in each pipe
- Expected tank levels (cumulative, based on inflows/outflows)
```

**Key Point**: EPANET uses Extended Period Simulation, which means:
- Tank levels change cumulatively over time (not reset each time)
- Network state is preserved between steps
- Patterns are applied based on current hour (2 PM = hour 14)

#### Step 2: Generate Actual SCADA Readings

```
SCADA Simulator generates:
- Pressure sensor readings (at junctions/tanks)
- Flow sensor readings (in pipes)
- Tank level readings (in tanks)

Each reading includes:
- Real-time timestamp (2:05 PM)
- Sensor ID (e.g., "PRESSURE_29")
- Sensor type (pressure/flow/level)
- Value (baseline × pattern_multiplier × noise)
- Location ID
```

**Pattern Application**:
- Uses real-time hour (14 = 2 PM)
- Applies diurnal multiplier (afternoon low: 0.6x)
- Adds realistic noise (±2% pressure, ±3% flow, ±1% level)

#### Step 3: Update Tank Levels from SCADA

```
Optional step to improve accuracy:
- Uses actual tank level readings from SCADA
- Updates EPANET tank initial conditions
- Makes future predictions more accurate
```

#### Step 4: Compare and Detect Anomalies

```
For each sensor reading:

1. Get expected value from EPANET
2. Get actual value from SCADA
3. Calculate deviation:
   deviation = |actual - expected| / expected × 100%

4. Compare with threshold:
   - Pressure: 10% threshold
   - Flow: 15% threshold
   - Tank Level: 5% threshold

5. If deviation > threshold:
   → Flag as ANOMALY
   → Classify severity:
      - Medium: 1.0x - 1.5x threshold
      - High: 1.5x - 2.0x threshold
      - Critical: > 2.0x threshold
```

**Example**:
```
Sensor: PRESSURE_29
Expected: 45.2 m
Actual: 38.5 m
Deviation: |38.5 - 45.2| / 45.2 × 100% = 14.82%
Threshold: 10%
Result: ANOMALY (High severity - 1.48x threshold)
```

#### Step 5: Store SCADA Readings

```
All sensor readings stored in database:
- Timestamp
- Sensor ID, type, location
- Value
- Network ID
```

#### Step 6: Store Anomalies

```
Detected anomalies stored in database:
- Timestamp
- Sensor information
- Actual vs Expected values
- Deviation percentage
- Severity level
```

#### Step 7: Update Status

```
Update monitoring service status with:
- Last check time
- Total anomalies detected
- Current monitoring interval
- EPS synchronization status
- Status: "running"
```

#### Step 8: Wait for Next Interval

```
Sleep for 5 minutes (or configured interval)
Then repeat from Step 1
```

## Real-Time Synchronization

EPS synchronizes to real-time:

1. **On Start**: 
   - Record start time: `2:00 PM = hour 14`
   - Calculate catch-up: `14 hours × 60 = 840 minutes`
   - Advance EPS by 840 steps → EPS now at hour 14
   - EPS and real-time are synchronized!

2. **During Monitoring**:
   - Calculate elapsed time since start
   - Advance EPS to match elapsed time
   - EPS hour = (start_hour + elapsed_hours) % 24
   - Always stays in sync with real-time

### Example Timeline

```
Start: 2:00 PM (14:00)
├─ EPS catches up: 0 → 14 hours (840 steps)
├─ EPS hour: 14, Real-time hour: 14 ✓

After 5 minutes: 2:05 PM
├─ Elapsed: 5 minutes
├─ EPS advances: 14:00 → 14:05
├─ EPS hour: 14, Real-time hour: 14 ✓

After 1 hour: 3:00 PM
├─ Elapsed: 1 hour
├─ EPS advances: 14:05 → 15:05
├─ EPS hour: 15, Real-time hour: 15 ✓

After 24 hours: Next day 2:00 PM
├─ Elapsed: 24 hours
├─ EPS wraps: 14:00 (modulo 24 hours)
├─ EPS hour: 14, Real-time hour: 14 ✓
```

## Diurnal Patterns

Both EPANET and SCADA use the same 24-hour demand pattern:

```
Hour 0-5:   0.7-0.8  (Night - low demand)
Hour 6-7:   0.7-1.4  (Morning rise)
Hour 8-9:   1.4       (Morning peak - high demand)
Hour 10-11: 1.2-1.4   (Post-morning)
Hour 12-13: 0.8-1.0   (Midday)
Hour 14-17: 0.6-0.9   (Afternoon - low demand)
Hour 18-19: 0.9-1.3   (Evening peak - high demand)
Hour 20-23: 0.8-1.0   (Evening to night)
```

**How it works**:
- At 8 AM: Both EPANET and SCADA use 1.4x multiplier (morning peak)
- At 2 PM: Both use 0.6x multiplier (afternoon low)
- Patterns always match because both use real-time hour

## Anomaly Detection

### Thresholds

| Sensor Type | Threshold | Example |
|------------|-----------|---------|
| Pressure   | 10%       | Expected: 45 m, Actual: 40 m → 11% deviation → **Anomaly** |
| Flow       | 15%       | Expected: 100 L/s, Actual: 120 L/s → 20% deviation → **Anomaly** |
| Tank Level | 5%        | Expected: 10 m, Actual: 9.4 m → 6% deviation → **Anomaly** |

### Severity Levels

| Severity | Range | Example (Pressure, 10% threshold) |
|----------|-------|-----------------------------------|
| Medium   | 1.0x - 1.5x | 10% - 15% deviation |
| High     | 1.5x - 2.0x | 15% - 20% deviation |
| Critical | > 2.0x      | > 20% deviation |

### What Causes Anomalies?

In real systems, anomalies indicate:
- **Leaks**: Pressure drops, flow increases
- **Pipe breaks**: Significant pressure/flow changes
- **Pump failures**: Flow/pressure drops
- **Sensor malfunctions**: Readings don't match expected
- **Demand spikes**: Unusual consumption patterns
- **Valve issues**: Flow restrictions or blockages

## Data Storage

### SCADA Readings Table

Stores all sensor readings over time:
```sql
scada_readings (
    id,
    network_id,
    timestamp,        -- When reading was taken
    sensor_id,        -- e.g., "PRESSURE_29"
    sensor_type,      -- "pressure", "flow", "level"
    value,            -- Actual sensor reading
    location_id       -- Node or link ID
)
```

**Storage Rate**: 
- Every 5 minutes (monitoring interval)
- All sensors at once (pressures + flows + tank levels)
- Example: 200 sensors × 12 readings/hour = 2,400 rows/hour

### Anomalies Table

Stores detected anomalies:
```sql
anomalies (
    id,
    network_id,
    timestamp,
    sensor_id,
    sensor_type,
    location_id,
    actual_value,      -- What sensor reported
    expected_value,    -- What EPANET predicted
    deviation_percent,  -- How much they differ
    threshold,         -- Threshold for this sensor type
    severity           -- "medium", "high", "critical"
)
```




## Process Status

Both the **SCADA Simulator** and **Monitoring Service** maintain their own independent status that is continuously updated and accessible from the frontend.

### Status States

Each process can be in one of the following states:
- **`stopped`**: Process is not running
- **`starting`**: Process is initializing
- **`running`**: Process is actively running
- **`error`**: Process encountered an error and stopped

### SCADA Simulator Status

The SCADA simulator status includes:

```json
{
  "status": "running" | "stopped" | "starting" | "error",
  "network_id": "uuid",
  "started_at": "2024-01-15T14:00:00Z",
  "last_generation_time": "2024-01-15T14:05:00Z",
  "total_readings_generated": 1420,
  "configuration": {
    "generation_rate_minutes": 5,
    "data_loss_proportion": 0.90,
    "delay_mean_minutes": 2.5,
    "delay_std_dev_minutes": 2.0,
    "delay_max_minutes": 10.0
  },
  "current_cycle": {
    "junctions_selected": 135,
    "pipes_selected": 180,
    "tanks_selected": 5,
    "readings_generated": 320
  },
  "error": null | "error message"
}
```

**Status Updates**:
- Updated after each generation cycle
- Includes real-time statistics
- Accessible via API endpoint: `GET /api/scada-simulator/status`

### Monitoring Service Status

The monitoring service status includes:

```json
{
  "status": "running" | "stopped" | "starting" | "error",
  "network_id": "uuid",
  "started_at": "2024-01-15T14:00:00Z",
  "last_check_time": "2024-01-15T14:05:00Z",
  "total_anomalies_detected": 12,
  "configuration": {
    "monitoring_interval_minutes": 5,
    "pressure_threshold_percent": 10.0,
    "flow_threshold_percent": 15.0,
    "tank_level_threshold_percent": 5.0
  },
  "eps_synchronization": {
    "synced": true,
    "current_eps_hour": 14,
    "real_time_hour": 14,
    "elapsed_minutes": 5
  },
  "last_check_stats": {
    "readings_processed": 320,
    "anomalies_found": 2,
    "comparison_time_ms": 1250
  },
  "error": null | "error message"
}
```

**Status Updates**:
- Updated after each monitoring cycle
- Includes EPS synchronization status
- Accessible via API endpoint: `GET /api/monitoring/status`

### Frontend Status Display

The frontend can:
- **Query status** via API endpoints (polling or WebSocket)
- **Display real-time status** for both processes
- **Show configuration** currently in use
- **Display statistics** (readings generated, anomalies detected, etc.)
- **Indicate process state** with visual indicators (running/stopped/error)

**Example Frontend Status Display**:
```
┌─────────────────────────────────┐
│ SCADA Simulator                 │
│ Status: 🟢 Running              │
│ Last Generation: 2:05 PM       │
│ Total Readings: 1,420          │
│ Config: 5 min, 90%, delay: 2.5±2.0 (max: 10)│
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Monitoring Service               │
│ Status: 🟢 Running              │
│ Last Check: 2:05 PM             │
│ Anomalies Detected: 12          │
│ EPS: Synced (Hour 14)           │
└─────────────────────────────────┘
```

### Status Storage

Process status can be:
- **In-memory**: Fast access, lost on restart
- **Database**: Persistent, survives restarts
- **Hybrid**: In-memory for speed, database for persistence

**Recommendation**: Store status in database for persistence and queryability, with in-memory cache for fast frontend access.

## Key Features

### 1. Real-Time Synchronization
- EPS starts at current real-time hour
- Stays synchronized throughout monitoring
- Patterns match between EPANET and SCADA

### 2. Cumulative Tank Level Tracking
- EPS maintains tank levels over time
- Accounts for inflows/outflows
- More accurate than snapshot analysis (which would reset tank levels each time)

### 3. Configurable Monitoring
- Adjustable monitoring interval (default: 5 minutes)
- Configurable anomaly thresholds
- Multiple networks can run simultaneously

### 4. Comprehensive Data Storage
- All SCADA readings stored
- All anomalies tracked
- Time-series database for efficient queries

### 5. Independent Process Status
- SCADA Simulator maintains its own status (running/stopped/error)
- Monitoring Service maintains its own status (running/stopped/error)
- Status accessible from frontend via API endpoints
- Real-time statistics and configuration visible
- Process states can be monitored independently

## Example Scenario

**Setup**:
- Network: 150 junctions, 200 pipes, 5 tanks
- Start time: 2:00 PM (14:00)
- Monitoring interval: 5 minutes

**What Happens**:

1. **2:00 PM - Start**:
   - EPS catches up: 0 → 14 hours (840 steps, takes ~10 seconds)
   - EPS now at hour 14, matching real-time
   - Monitoring loop begins

2. **2:05 PM - First Check**:
   - EPANET: Calculates expected values at hour 14:05
   - SCADA: Generates readings using hour 14 patterns (afternoon low: 0.6x)
   - Comparison: No anomalies (values match within thresholds)
   - Storage: 355 readings stored (150 pressures + 200 flows + 5 levels)

3. **2:10 PM - Second Check**:
   - EPANET: Advances to 14:10
   - SCADA: Generates new readings
   - Comparison: 1 anomaly detected (pressure drop at junction 29)
   - Storage: 355 readings + 1 anomaly stored

4. **Continues every 5 minutes...**

5. **Next Day 2:00 PM**:
   - EPS wraps around (24 hours elapsed)
   - EPS hour: 14, Real-time hour: 14
   - Still synchronized!

## Summary

The monitoring system:
- ✅ Runs continuously in the background
- ✅ Uses EPANET hydraulic analysis to predict expected values (real network analysis)
- ✅ Generates realistic SCADA sensor readings (simulated until real sensors are connected)
- ✅ Synchronizes EPANET Extended Period Simulation to real-time
- ✅ Compares expected vs actual values
- ✅ Detects anomalies with configurable thresholds
- ✅ Stores all data in database
- ✅ Handles errors gracefully
- ✅ Supports multiple networks simultaneously

**Important Note**: This is a **monitoring system** for **real water networks**. The only simulated component is the SCADA sensor readings (because real sensors aren't connected yet). EPANET performs real hydraulic analysis of the actual network to predict what values should be. When real SCADA sensors are connected, simply replace the SCADA simulator with real sensor data.

