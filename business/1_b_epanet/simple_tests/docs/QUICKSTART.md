# Quick Start Guide
## Water Network Monitoring System

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

#### 1. Install Required Python Packages

```bash
pip install -r requirements.txt
```

This will install:
- epyt (EPANET Python Toolkit)
- dash (Web dashboard framework)
- plotly (Visualization library)
- numpy (Numerical computing)

#### 2. Verify Installation

```bash
python test_system.py
```

You should see:
```
✓ All tests passed! System is ready to run.
```

### Running the System

#### Option 1: Use Example Network (Net1.inp)

```bash
python main_monitor.py
```

#### Option 2: Use Yasmin Network

```bash
python main_monitor.py /path/to/yasmin.inp
```

### Accessing the Dashboard

1. Wait for the message: `Dashboard URL: http://localhost:8050`
2. Open your web browser
3. Navigate to: `http://localhost:8050`

### What You'll See

The dashboard displays:

1. **Header**
   - System status
   - Current simulation time
   - Number of active sensors

2. **Network Map** (Left panel)
   - Visual representation of the network
   - Color-coded nodes showing pressure levels
   - Interactive tooltips with node/link information

3. **Alerts Panel** (Right panel)
   - Real-time system alerts
   - Pressure warnings
   - Network statistics

4. **Trend Charts** (Bottom)
   - Pressure trends over time
   - Flow trends over time

### Understanding the Simulation

- The simulation runs in steps (default: 50 steps)
- Each step represents one hydraulic time step (usually 1 hour)
- The dashboard updates every 2 seconds
- Sensor data includes realistic noise to simulate real conditions

### Customization

Edit `main_monitor.py` to change:

```python
MAX_STEPS = 50              # Number of simulation steps
UPDATE_INTERVAL = 1.0       # Seconds between updates
DASHBOARD_PORT = 8050       # Web server port
```

### Stopping the System

Press `Ctrl+C` in the terminal window

### Troubleshooting

#### Problem: "Module not found" errors
**Solution:** Install missing packages
```bash
pip install -r requirements.txt
```

#### Problem: "Port already in use"
**Solution:** Change the port in `main_monitor.py`
```python
DASHBOARD_PORT = 8051  # Use different port
```

#### Problem: Network file not found
**Solution:** Use absolute path to .inp file
```bash
python main_monitor.py /full/path/to/yasmin.inp
```

#### Problem: Dashboard not loading
**Solution:** Check firewall settings and ensure port 8050 is accessible

### Next Steps

1. **Experiment with Yasmin Network**
   - Place yasmin.inp in the project directory
   - Run: `python main_monitor.py yasmin.inp`

2. **Adjust Sensor Placement**
   - Edit `scada_simulator.py`
   - Modify `auto_deploy_sensors()` method

3. **Customize Dashboard**
   - Edit `network_dashboard.py`
   - Modify alert thresholds
   - Change color schemes
   - Add new visualizations

4. **Export Data**
   - Add database integration
   - Save results to CSV/JSON
   - Generate reports

### Getting Help

- Check `README.md` for detailed documentation
- Review `docs/epyt_api.md` for EPyT functions
- See `docs/project_description.md` for system architecture

### Example Session

```bash
# Terminal output when running
$ python main_monitor.py

============================================================
🌊 Water Network Monitoring System
============================================================
Loading network: Net1.inp
✓ Network loaded successfully

Network Information:
  - Total Nodes: 11
  - Junctions: 9
  - Reservoirs: 1
  - Tanks: 1
  - Total Links: 12
  - Pipes: 12
  - Pumps: 1
  - Valves: 0
  - Simulation Duration: 24.0 hours

Initializing system components...
Auto-deployed sensors:
  - 10 pressure sensors at nodes: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  - 5 flow sensors at links: [1, 3, 5, 7, 9]
  - 1 level sensors at tanks: [2]
✓ System initialization complete

============================================================
🌊 Starting Water Network Dashboard
============================================================
Dashboard URL: http://localhost:8050
Press Ctrl+C to stop the server
============================================================

Dash is running on http://0.0.0.0:8050/

 * Serving Flask app 'network_dashboard'
 * Debug mode: off

============================================================
Starting simulation loop...
Max steps: 50
Update interval: 1.0s
============================================================

  Step 5/50: t = 05:00:00
  Step 10/50: t = 10:00:00
  ...
```

### Success Checklist

- [ ] Python 3.7+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Test system passes (`python test_system.py`)
- [ ] Dashboard accessible at http://localhost:8050
- [ ] Network visualization displays correctly
- [ ] Real-time updates working
- [ ] Alerts functioning

🎉 **Congratulations!** Your water network monitoring system is running!
