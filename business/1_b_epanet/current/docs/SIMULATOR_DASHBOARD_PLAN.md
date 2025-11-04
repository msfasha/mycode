# Simulator Dashboard Implementation Plan

## Overview
Implement a minimal viable monitoring dashboard on the Simulator page to provide real-time visibility into the monitoring process.

## Phase 1: Minimal Dashboard (Current Implementation)

### Components to Build

**1. Simulation Status Card** (`SimulationStatus.tsx`)
- Current status (Running/Stopped/Error)
- Start time & elapsed duration  
- Monitoring interval (e.g., "5 minutes")
- Network ID display
- Basic network info (junctions, pipes count)

**2. Monitoring Statistics Card** (`MonitoringStats.tsx`)
- Total comparisons performed (monitoring cycles)
- Total anomalies detected (session total)
- Anomaly breakdown by severity:
  - Critical count (red badge)
  - High count (orange badge)  
  - Medium count (yellow badge)
- Anomaly detection rate (% of readings with anomalies)

**3. Recent Anomalies Table** (`AnomaliesTable.tsx`)
- Table showing last 10-15 anomalies
- Columns: Timestamp, Sensor ID, Type, Location, Expected, Actual, Deviation %, Severity
- Color-coded severity badges
- Auto-refresh every 5-10 seconds when simulation running
- Click to view details (future)

**4. Latest Cycle Info** (`LatestCycleInfo.tsx` - Optional)
- Current monitoring cycle number
- Last update timestamp
- Next cycle countdown (if running)
- Database storage status (readings/anomalies stored)

### Backend API Additions

**New Endpoint: GET /api/simulation/stats/{network_id}**
```json
{
  "network_id": "uuid",
  "total_comparisons": 120,
  "total_anomalies": 45,
  "anomalies_by_severity": {
    "critical": 5,
    "high": 12,
    "medium": 28
  },
  "anomaly_rate": 37.5,
  "latest_timestamp": "2024-10-29T21:44:12",
  "simulation_running": true
}
```

**Modify: GET /api/simulation/anomalies/{network_id}**
- Already exists, use with `limit=15` for recent anomalies
- Ensure sorted by timestamp DESC

### Implementation Steps

1. **Backend Enhancement**
   - Add `get_simulation_stats()` function in `backend/api/simulation.py`
   - Query database for aggregated anomaly statistics
   - Calculate anomaly rates

2. **Frontend Components**
   - Create 4 new components (Status, Stats, AnomaliesTable, CycleInfo)
   - Add polling logic in SimulatorPage (fetch every 5-10 seconds)
   - Integrate components into SimulatorPage layout

3. **Styling & UX**
   - Use existing color scheme
   - Severity color coding: Critical=red, High=orange, Medium=yellow
   - Responsive grid layout
   - Loading states for async data

### Files to Create/Modify

**Backend:**
- `backend/api/simulation.py` - Add stats endpoint

**Frontend:**
- `frontend/src/pages/SimulatorPage.tsx` - Integrate dashboard
- `frontend/src/components/SimulationStatus.tsx` - New
- `frontend/src/components/MonitoringStats.tsx` - New
- `frontend/src/components/AnomaliesTable.tsx` - New
- `frontend/src/components/LatestCycleInfo.tsx` - New (optional)




