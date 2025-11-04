# Water Network Monitoring System

A real-time water distribution network monitoring system using EPANET and EPyT for Jordan's water networks.

## Overview

This system provides:
- **Real-time hydraulic simulation** using EPANET
- **SCADA sensor simulation** with realistic noise
- **Interactive web dashboard** for network visualization
- **Automated alerts** for pressure anomalies
- **Historical trend analysis**

## Project Structure

```
.
├── main_monitor.py          # Main application entry point
├── scada_simulator.py       # SCADA sensor simulation
├── realtime_simulator.py    # Real-time EPANET simulation engine
├── network_dashboard.py     # Plotly Dash web dashboard
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify EPANET Installation

The system uses EPyT (EPANET Python Toolkit). Make sure it's properly installed:

```bash
python -c "from epyt import epanet; print('EPyT installed successfully')"
```

## Usage

### Basic Usage (with Net1.inp example)

```bash
python main_monitor.py
```

### Using Your Own Network (Yasmin Network)

```bash
python main_monitor.py /path/to/yasmin.inp
```

### Access the Dashboard

Once running, open your browser and navigate to:
```
http://localhost:8050
```

## Features

### 1. SCADA Simulation

The `SCADASimulator` class simulates sensor readings:
- **Pressure sensors** at junctions
- **Flow meters** at pipes
- **Level sensors** at tanks
- **Realistic noise** added to readings

### 2. Real-Time Simulation

The `RealTimeSimulator` class manages:
- Step-by-step hydraulic analysis
- Historical data collection
- State management
- Time progression

### 3. Interactive Dashboard

The `NetworkDashboard` provides:
- **Network map** with color-coded pressures
- **Pressure trends** over time
- **Flow trends** over time
- **Real-time alerts** for anomalies
- **System statistics**

## Configuration

Edit `main_monitor.py` to customize:

```python
# Configuration
INP_FILE = "Net1.inp"        # Your EPANET network file
MAX_STEPS = 50               # Number of simulation steps
UPDATE_INTERVAL = 1.0        # Seconds between updates
DASHBOARD_PORT = 8050        # Dashboard web port
```

## Dashboard Components

### Status Panel
- System operational status
- Current simulation time
- Active sensor count

### Network Map
- Node visualization (junctions, tanks, reservoirs)
- Color-coded pressure levels
- Flow visualization on links
- Interactive tooltips

### Alerts Panel
- Low pressure warnings (< 20m)
- High pressure warnings (> 100m)
- System status indicators

### Statistics Panel
- Average/Min/Max pressures
- Total flow and demand
- Network size information

### Trend Charts
- Pressure trends for selected nodes
- Flow trends for selected links
- Historical data visualization

## System Architecture

```
┌─────────────────┐
│  EPANET Model   │
│   (yasmin.inp)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ RealTimeSimulator   │
│ - Hydraulic Engine  │
│ - State Management  │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────┐      ┌─────────────────┐
│  SCADASimulator      │◄─────┤  Sensor Data    │
│  - Virtual Sensors   │      │  - Pressure     │
│  - Noise Generation  │      │  - Flow         │
└──────────┬───────────┘      │  - Tank Levels  │
           │                  └─────────────────┘
           ▼
┌──────────────────────┐
│  NetworkDashboard    │
│  - Web Interface     │
│  - Visualization     │
│  - Alerts            │
└──────────────────────┘
```

## Future Enhancements

### For Production Deployment

1. **Real SCADA Integration**
   - OPC-UA protocol support
   - Modbus TCP/RTU integration
   - REST API endpoints

2. **Database Integration**
   - TimescaleDB for time-series data
   - Historical data storage
   - Data analytics

3. **Advanced Features**
   - Machine learning anomaly detection
   - Predictive maintenance
   - Water quality tracking (MSX)
   - Demand forecasting

4. **Mobile Support**
   - SMS/Email alerts
   - Mobile app interface
   - Push notifications

5. **GIS Integration**
   - Real map overlay (OpenStreetMap)
   - GPS coordinates
   - Spatial analysis

## Requirements

- Python 3.7+
- EPyT (EPANET Python Toolkit)
- Dash & Plotly
- NumPy
- EPANET 2.2+

## Troubleshooting

### EPyT Import Error
```bash
pip install epyt --upgrade
```

### Dashboard Not Loading
- Check port 8050 is not in use
- Try different port in configuration
- Check firewall settings

### Network File Not Found
- Verify .inp file path is correct
- Use absolute path if needed
- Check file permissions

## Support

For issues related to:
- **EPANET**: https://github.com/OpenWaterAnalytics/EPANET
- **EPyT**: https://github.com/KIOS-Research/EPyT

## License

This project uses:
- EPANET (Public Domain - US EPA)
- EPyT (EUPL v1.2)

## Contact

For deployment in Jordan's water networks, ensure:
1. Network calibration with real data
2. Sensor placement optimization
3. Integration with existing SCADA systems
4. Regulatory compliance
