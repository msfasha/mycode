# Water Network Monitoring System - Project Description

## Project Overview

A real-time dynamic water network monitoring system for water distribution networks in Jordan, specifically designed for the Yasmin region in Amman. The system uses EPANET hydraulic modeling combined with simulated SCADA sensors and an interactive web dashboard.

## Goals

1. **Immediate**: Build and test a prototype monitoring system using simulated SCADA data
2. **Short-term**: Validate system with Yasmin network (yasmin.inp) from Amman
3. **Long-term**: Deploy framework in real environments to monitor Jordan's water networks

## System Components

### 1. Core Modules

#### `scada_simulator.py`
- Simulates SCADA sensor readings from EPANET simulation
- Supports pressure, flow, and tank level sensors
- Adds realistic sensor noise
- Auto-deployment of sensors at strategic locations

#### `realtime_simulator.py`
- Manages continuous hydraulic simulation
- Step-by-step execution of EPANET engine
- Historical data collection
- State management and time progression

#### `network_dashboard.py`
- Interactive web dashboard using Plotly Dash
- Real-time network visualization
- Pressure and flow trend charts
- Automated alert system
- Network statistics display

#### `main_monitor.py`
- Main application entry point
- Integrates all components
- Threading for concurrent simulation and dashboard
- Configuration management

### 2. Supporting Files

- `requirements.txt` - Python dependencies
- `test_system.py` - System component verification
- `README.md` - User documentation
- `epyt_api.md` - EPyT API reference

## Key Features

### Real-Time Monitoring
- Continuous hydraulic simulation
- Live sensor data (simulated)
- Automatic state updates
- Historical trend tracking

### Interactive Dashboard
- Network map with color-coded pressures
- Real-time alerts for anomalies
- Pressure and flow trends
- System statistics
- Responsive web interface

### SCADA Simulation
- Configurable sensor placement
- Realistic noise generation
- Multiple sensor types (pressure, flow, level)
- Auto-deployment capability

### Alert System
- Low pressure detection (< 20m)
- High pressure warnings (> 100m)
- Real-time notifications
- Visual indicators

## Technology Stack

- **EPANET 2.2+**: Hydraulic modeling engine
- **EPyT**: Python interface for EPANET
- **Plotly Dash**: Web dashboard framework
- **NumPy**: Numerical computations
- **Python 3.7+**: Core programming language

## Deployment Roadmap

### Phase 1: Prototype (Current)
- ✓ SCADA simulation
- ✓ Real-time hydraulic engine
- ✓ Interactive dashboard
- ✓ Basic alert system

### Phase 2: Integration (Next)
- Database integration (TimescaleDB/InfluxDB)
- GIS integration (OpenStreetMap overlay)
- Enhanced visualization
- Mobile-responsive design

### Phase 3: Production (Future)
- Real SCADA integration (OPC-UA, Modbus)
- Machine learning anomaly detection
- Predictive maintenance
- SMS/Email alerts
- Water quality tracking (MSX)
- Multi-user support
- Role-based access control

## Usage

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Test system
python test_system.py

# Run with example network
python main_monitor.py

# Run with Yasmin network
python main_monitor.py yasmin.inp
```

### Access Dashboard
Open browser: `http://localhost:8050`

## Configuration

Edit `main_monitor.py`:
```python
INP_FILE = "yasmin.inp"     # Network file
MAX_STEPS = 50              # Simulation steps
UPDATE_INTERVAL = 1.0       # Update frequency (seconds)
DASHBOARD_PORT = 8050       # Web port
```

## Future Enhancements

### SCADA Integration
- OPC-UA protocol support
- Modbus TCP/RTU integration
- REST API endpoints
- Real-time data validation

### Advanced Analytics
- Demand forecasting
- Leak detection algorithms
- Pressure management optimization
- Energy efficiency analysis

### Operational Features
- Historical data analysis
- Report generation
- Multi-network support
- User management system

### Mobile & Alerts
- Mobile application
- Push notifications
- SMS/Email alerts
- Customizable thresholds

## References

- EPANET Documentation: https://github.com/OpenWaterAnalytics/EPANET
- EPyT Documentation: https://github.com/KIOS-Research/EPyT
- EPyT API Reference: See `docs/epyt_api.md`

## License

- EPANET: Public Domain (US EPA)
- EPyT: EUPL v1.2

## Contact & Support

For deployment in Jordan's water networks:
- Ensure network calibration with real data
- Optimize sensor placement
- Integrate with existing SCADA infrastructure
- Comply with local regulations

GitHub Copilot: I'll read the API documentation in the docs folder for you. 

Read [](file:///media/me/Active/mywork/coding/mycode/code_experiments/0_epanet/simple_vscode/docs/epyt_api.md#1-1), lines 1 to 100

Let me continue reading more of the documentation to get a better overview: 

Read [](file:///media/me/Active/mywork/coding/mycode/code_experiments/0_epanet/simple_vscode/docs/epyt_api.md#100-100), lines 100 to 500

Let me read a bit more to get a complete picture of the API capabilities: 

Read [](file:///media/me/Active/mywork/coding/mycode/code_experiments/0_epanet/simple_vscode/docs/epyt_api.md#500-500), lines 500 to 1000

Based on my reading of the EPYT API documentation, here's a comprehensive summary:

## EPYT API - EPANET Python Toolkit

### Overview
**EPyT (EPANET-Python Toolkit)** is a Python interface for EPANET libraries, which models water distribution piping systems. It was developed by KIOS Research and Innovation Center of Excellence at the University of Cyprus.

### Basic Usage
```python
from epyt import epanet
d = epanet('Net1.inp')
```

### Key Features & Capabilities

#### 1. **Network Components Management**
- **Nodes**: Add/modify junctions, reservoirs, and tanks
- **Links**: Add/modify pipes, pumps, and various valve types (PRV, PSV, FCV, TCV, GPV, PBV, CV)
- **Controls**: Simple time-based and condition-based controls
- **Rules**: Rule-based controls for complex logic
- **Patterns**: Time patterns for demands and operations
- **Curves**: Pump curves, efficiency curves, volume curves

#### 2. **Analysis Types**
- **Hydraulic Analysis**: Flow, pressure, velocity calculations
- **Water Quality Analysis**: Chemical/age tracking through the network
- **Extended Period Simulation**: Time-based simulations
- **MSX (Multi-Species Extension)**: Advanced water quality modeling

#### 3. **Data Retrieval Methods** (Get functions)
The API provides extensive getter methods for:
- Node properties (pressure, elevation, demand, coordinates, etc.)
- Link properties (flow, velocity, diameter, roughness, status, etc.)
- Network-wide statistics
- Simulation results over time
- Control and rule information
- Pattern and curve data

#### 4. **Data Modification Methods** (Set functions)
- Modify node properties (elevations, demands, coordinates)
- Change link properties (diameter, roughness, status, settings)
- Update controls and rules
- Modify patterns and curves
- Change simulation options and parameters

#### 5. **Visualization**
- `plot()` method for network visualization
- Can highlight specific nodes/links
- Network transformation functions:
  - `appRotateNetwork()`: Rotate network by angle
  - `appShiftNetwork()`: Translate network coordinates

#### 6. **Data Export**
The `EpytValues` class provides methods to export results:
- `to_dict()`: Convert to dictionary
- `to_json()`: Export to JSON format
- `to_excel()`: Save to Excel files
- `disp()`: Display in command window

#### 7. **Key Constants**
The toolkit includes numerous EPANET constants for:
- Node types (junction, reservoir, tank)
- Link types (pipe, pump, valve types)
- Units (flow, pressure, etc.)
- Control types
- Quality analysis parameters
- Simulation settings

#### 8. **Common Operations**
- **Adding components**: `addNodeJunction()`, `addLinkPipe()`, `addLinkPump()`, `addLinkValve*()`
- **Deleting components**: `deleteNode()`, `deleteLink()`, `deleteControls()`, `deleteRules()`
- **Running simulations**: Hydraulic and quality analysis methods
- **Report generation**: `writeReport()`, `clearReport()`, `copyReport()`

### Architecture
- Based on EPANET engine by US EPA
- Supports EPANET versions 2.2+
- Can use custom library paths
- Inspired by EPANET-MATLAB Toolkit
- Licensed under EUPL v1.2

This is a comprehensive toolkit for programmatic water distribution network modeling, analysis, and optimization in Python.

msfasha: I want to build a dynamic water network monitoring system using epanet.
Eventually, i want to be able to deploy this framework in real environments to monitor water networks in Jordan.
I have yasmin.inp network file for a region in Amman, and i want to use that network to build the test the system
We need to feed it with live information from related systems e.g. scada and sensors
I have no scada access right now, so i want to simulate it and build this dynamic monitoring model.
I want to start this continuous monitoring and display the state of the network using dashboards and images of maps of the network.
You can refer to the internet as well as the documents in the docs folder for ideas and information about epanet and epyt capabilities.
You thoughts please.

Workspace: Collecting workspace informationThis is an excellent project! Building a dynamic water network monitoring system for Jordan using EPANET is very valuable. Let me provide you with a comprehensive approach based on EPyT capabilities and best practices.

## System Architecture Overview

Based on the epyt_api.md documentation and your requirements, here's my recommended approach:

### 1. **Data Acquisition Layer (SCADA Simulation)**

Since you don't have real SCADA access yet, you'll need to simulate sensor data:

```python
import numpy as np
from datetime import datetime, timedelta
import pandas as pd

class SCADASimulator:
    """Simulates SCADA sensor readings from EPANET hydraulic simulation"""
    
    def __init__(self, epanet_model):
        self.d = epanet_model
        self.sensor_locations = {
            'pressure': [],  # Node indices with pressure sensors
            'flow': [],      # Link indices with flow sensors
            'level': []      # Tank indices with level sensors
        }
    
    def add_sensors(self, node_indices=None, link_indices=None, tank_indices=None):
        """Add virtual sensors at specific locations"""
        if node_indices:
            self.sensor_locations['pressure'] = node_indices
        if link_indices:
            self.sensor_locations['flow'] = link_indices
        if tank_indices:
            self.sensor_locations['level'] = tank_indices
    
    def get_live_data(self, add_noise=True):
        """Simulate real-time sensor readings with optional noise"""
        data = {
            'timestamp': datetime.now(),
            'pressure': {},
            'flow': {},
            'tank_level': {}
        }
        
        # Get pressure readings
        pressures = self.d.getNodePressure()
        for idx in self.sensor_locations['pressure']:
            value = pressures[idx-1]
            if add_noise:
                value += np.random.normal(0, 0.5)  # Add sensor noise
            data['pressure'][f'Node_{idx}'] = value
        
        # Get flow readings
        flows = self.d.getLinkFlows()
        for idx in self.sensor_locations['flow']:
            value = flows[idx-1]
            if add_noise:
                value += np.random.normal(0, 2.0)
            data['flow'][f'Link_{idx}'] = value
        
        # Get tank levels
        tank_levels = self.d.getNodeTankInitialLevel()
        for i, idx in enumerate(self.sensor_locations['level']):
            value = tank_levels[i]
            if add_noise:
                value += np.random.normal(0, 0.1)
            data['tank_level'][f'Tank_{idx}'] = value
        
        return data
```

### 2. **Real-Time Hydraulic Analysis Engine**

Use EPyT's step-by-step simulation capabilities (see epyt_api.md line 1562):

```python
class RealTimeSimulator:
    """Manages continuous hydraulic and quality simulation"""
    
    def __init__(self, inp_file):
        self.d = epanet(inp_file)
        self.current_time = 0
        self.time_history = []
        self.pressure_history = []
        self.flow_history = []
        
    def initialize(self):
        """Initialize hydraulic analysis"""
        self.d.openHydraulicAnalysis()
        self.d.initializeHydraulicAnalysis()
        
    def step(self):
        """Advance simulation by one hydraulic time step"""
        t = self.d.runHydraulicAnalysis()
        
        # Collect current state
        current_state = {
            'time': t,
            'pressures': self.d.getNodePressure(),
            'flows': self.d.getLinkFlows(),
            'demands': self.d.getNodeActualDemand(),
            'tank_levels': self.d.getNodeHydraulicHead(self.d.getNodeTankIndex())
        }
        
        # Store history
        self.time_history.append(t)
        self.pressure_history.append(current_state['pressures'])
        self.flow_history.append(current_state['flows'])
        
        # Advance to next time step
        tstep = self.d.nextHydraulicAnalysisStep()
        
        return current_state, tstep
    
    def run_continuous(self, duration_hours=24, callback=None):
        """Run continuous simulation with optional callback for each step"""
        self.initialize()
        tstep = 1
        
        while tstep > 0:
            state, tstep = self.step()
            
            if callback:
                callback(state)
        
        self.d.closeHydraulicAnalysis()
```

### 3. **State Estimation & Data Assimilation**

For real deployment, you'll need to merge simulated and measured data (see RTX Extension docs):

```python
class StateEstimator:
    """Combines EPANET model with sensor measurements"""
    
    def __init__(self, model, scada_sim):
        self.model = model
        self.scada = scada_sim
        
    def update_model_with_measurements(self, sensor_data):
        """Update EPANET model with real sensor readings"""
        
        # Update boundary conditions (tank levels, reservoir heads)
        for tank_name, level in sensor_data.get('tank_level', {}).items():
            tank_idx = self.model.getNodeIndex(tank_name.replace('Tank_', ''))
            self.model.setNodeTankInitialLevel(tank_idx, level)
        
        # Update demands based on flow measurements (demand estimation)
        # This is simplified - real implementation would use optimization
        for node_name, pressure in sensor_data.get('pressure', {}).items():
            # Adjust demands to match measured pressures
            pass
        
        return self.model
```

### 4. **Real-Time Dashboard**

Using Plotly Dash for interactive visualization:

```python
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import threading
import queue

class NetworkDashboard:
    """Real-time dashboard for water network monitoring"""
    
    def __init__(self, epanet_model):
        self.d = epanet_model
        self.app = dash.Dash(__name__)
        self.data_queue = queue.Queue()
        
        # Get network structure
        self.nodes = self.d.getNodeCoordinates()
        self.links = self.d.getNodesConnectingLinksIndex()
        
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Create dashboard layout"""
        self.app.layout = html.Div([
            html.H1('Yasmin Network - Real-Time Monitor'),
            
            dcc.Graph(id='network-map'),
            dcc.Graph(id='pressure-trend'),
            dcc.Graph(id='flow-trend'),
            
            dcc.Interval(
                id='interval-component',
                interval=5*1000,  # Update every 5 seconds
                n_intervals=0
            ),
            
            html.Div(id='alerts')
        ])
    
    def setup_callbacks(self):
        """Setup real-time update callbacks"""
        
        @self.app.callback(
            [Output('network-map', 'figure'),
             Output('pressure-trend', 'figure'),
             Output('alerts', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_graphs(n):
            # Get latest data
            try:
                data = self.data_queue.get_nowait()
            except queue.Empty:
                return dash.no_update
            
            # Create network map with color-coded pressures
            network_fig = self.create_network_figure(data)
            
            # Create pressure trend chart
            pressure_fig = self.create_pressure_trend(data)
            
            # Check for alerts
            alerts = self.check_alerts(data)
            
            return network_fig, pressure_fig, alerts
    
    def create_network_figure(self, data):
        """Create network visualization with current state"""
        pressures = data.get('pressures', [])
        
        # Create node trace with color-coded pressures
        node_trace = go.Scatter(
            x=[coord[0] for coord in self.nodes[0]],
            y=[coord[1] for coord in self.nodes[1]],
            mode='markers',
            marker=dict(
                size=10,
                color=pressures,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Pressure (m)")
            ),
            text=[f'Node {i+1}: {p:.2f} m' for i, p in enumerate(pressures)],
            hoverinfo='text'
        )
        
        # Create link traces
        link_traces = []
        for link_idx in range(len(self.links[0])):
            from_node = self.links[0][link_idx] - 1
            to_node = self.links[1][link_idx] - 1
            
            link_traces.append(go.Scatter(
                x=[self.nodes[0][from_node], self.nodes[0][to_node]],
                y=[self.nodes[1][from_node], self.nodes[1][to_node]],
                mode='lines',
                line=dict(color='gray', width=1),
                hoverinfo='skip'
            ))
        
        return {
            'data': link_traces + [node_trace],
            'layout': go.Layout(
                title='Network Status',
                showlegend=False,
                hovermode='closest',
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False)
            )
        }
    
    def check_alerts(self, data):
        """Check for operational alerts"""
        alerts = []
        
        pressures = data.get('pressures', [])
        min_pressure = 20  # minimum required pressure in meters
        
        for i, p in enumerate(pressures):
            if p < min_pressure:
                alerts.append(
                    html.Div(f'⚠️ Low pressure at Node {i+1}: {p:.2f} m',
                            style={'color': 'red', 'fontWeight': 'bold'})
                )
        
        return alerts if alerts else html.Div('✓ All systems normal', 
                                              style={'color': 'green'})
    
    def run(self, port=8050):
        """Start the dashboard server"""
        self.app.run_server(debug=True, port=port)
```

### 5. **Complete Integration**

Here's how to put it all together:

```python
# main_monitor.py
from epyt import epanet
import time
import threading

def main():
    # Load Yasmin network
    inp_file = '//media//me//Active//mywork//coding//mycode//code_experiments//0_epanet//niho_inp//yasmin.inp'
    d = epanet(inp_file)
    
    # Setup simulation
    simulator = RealTimeSimulator(inp_file)
    
    # Setup SCADA simulator with sensors at critical points
    scada = SCADASimulator(d)
    scada.add_sensors(
        node_indices=[1, 5, 10, 15],  # Example: Add pressure sensors
        link_indices=[1, 3, 7],        # Example: Add flow meters
        tank_indices=d.getNodeTankIndex()  # Monitor all tanks
    )
    
    # Setup dashboard
    dashboard = NetworkDashboard(d)
    
    # Run simulation in separate thread
    def simulation_loop():
        simulator.initialize()
        tstep = 1
        
        while tstep > 0:
            state, tstep = simulator.step()
            
            # Get simulated sensor data
            sensor_data = scada.get_live_data()
            sensor_data.update(state)
            
            # Push to dashboard
            dashboard.data_queue.put(sensor_data)
            
            time.sleep(1)  # Real-time pacing
        
        simulator.d.closeHydraulicAnalysis()
    
    # Start simulation thread
    sim_thread = threading.Thread(target=simulation_loop, daemon=True)
    sim_thread.start()
    
    # Start dashboard
    dashboard.run()

if __name__ == '__main__':
    main()
```

### 6. **Next Steps for Real Deployment**

1. **Database Integration**: Store historical data using TimescaleDB or InfluxDB
2. **SCADA Integration**: Replace `SCADASimulator` with real SCADA connectors (OPC-UA, Modbus, etc.)
3. **Machine Learning**: Add anomaly detection and predictive maintenance
4. **Mobile Alerts**: Integrate with SMS/email for critical alerts
5. **Water Quality**: Use MSX extension for chlorine/contaminant tracking (see epyt_api.md line 4200)

Would you like me to elaborate on any specific component or create working example code for the Yasmin network?