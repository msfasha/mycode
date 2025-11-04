# HydroTwin - EPANET Real-time Simulation

A comprehensive Python framework for real-time EPANET water distribution network simulation with SCADA integration, control logic, and monitoring capabilities.

## Features

### Web Application Features
- **Interactive Dashboard**: User-friendly web interface for all simulation operations
- **Real-time Monitoring**: Live updates of simulation progress and results
- **Interactive Plots**: Generated visualizations of pressure and flow data
- **Results Download**: Export simulation results as JSON files
- **Network File Management**: Browse and select from available network files
- **Responsive Design**: Works on desktop and mobile devices

### Simulation Features
- **Real-time Simulation**: Step-by-step hydraulic analysis with configurable time steps
- **Sensor Monitoring**: Virtual sensors for pressure, flow, and tank level monitoring
- **Control Logic**: Automated control systems based on sensor readings
- **SCADA Integration**: Database logging and real-time data integration
- **Performance Tracking**: Comprehensive metrics and reporting
- **Visualization**: Real-time plotting and data visualization

## Quick Start

### 1. Setup Environment

```bash
# Make the setup script executable and run it
chmod +x setup_environment.sh
./setup_environment.sh
```

### 2. Run Web Application (Recommended)

```bash
# Start the web application
./start_web_app.sh

# Or manually:
source venv/bin/activate
python app.py
```

Then open your browser and go to: **http://localhost:5000**

### 3. Run Command Line Examples

```bash
# Activate environment
source venv/bin/activate

# Run all examples
python run_examples.py

# Or run individual examples
python test_realtime.py          # Test suite
python simple_realtime.py       # Basic simulation
python advanced_realtime.py     # Advanced simulation with control logic
python scada_integration.py     # SCADA integration example
python realtime_simulation.py  # Comprehensive simulation
```

## Project Structure

```
HydroTwin/
├── realtime_simulation.py     # Main comprehensive simulator
├── simple_realtime.py         # Basic real-time simulation
├── advanced_realtime.py       # Advanced simulation with control logic
├── scada_integration.py      # SCADA system integration
├── test_realtime.py          # Test suite
├── run_examples.py           # Master runner script
├── requirements.txt          # Python dependencies
├── setup_environment.sh     # Environment setup script
└── README.md                # This file
```

## Examples Overview

### 1. Simple Real-time Simulation (`simple_realtime.py`)
- Basic step-by-step hydraulic analysis
- Minimal control logic
- Perfect for learning EPANET basics

### 2. Advanced Real-time Simulation (`advanced_realtime.py`)
- Sophisticated sensor monitoring
- Alarm system implementation
- Advanced control logic
- Performance metrics and visualization

### 3. SCADA Integration (`scada_integration.py`)
- Simulated SCADA data sources
- Database logging (SQLite)
- Real-time data integration
- Alert and control system logging

### 4. Comprehensive Simulation (`realtime_simulation.py`)
- Full-featured real-time simulator
- Complete sensor setup and monitoring
- Advanced control logic implementation
- Comprehensive reporting and visualization

## Dependencies

- **Python 3.8+**
- **epyt**: EPANET Python toolkit
- **numpy**: Numerical computations
- **matplotlib**: Plotting and visualization
- **pandas**: Data manipulation
- **scipy**: Scientific computing
- **sqlite3**: Database operations (built-in)

## Network Files

The examples use EPANET network files (`.inp` format) from the `water-networks/` directory:
- `water-networks/Net1.inp` - Main test network
- `water-networks/Net2.inp` - Additional network
- `water-networks/Net3.inp` - Additional network
- `water-networks/Net1_temp.inp` - Temporary network

You can modify the network file path in each script as needed.

## Output Files

The simulations generate several output files:
- **Plots**: `*_results.png` - Visualization plots
- **Data**: `*_data.json` - Simulation data in JSON format
- **Database**: `realtime_simulation.db` - SQLite database with logged data

## Customization

### Adding New Sensors
```python
# In the simulator class
def _setup_sensors(self):
    # Add your custom sensors here
    self.sensors['custom_sensor'] = {
        'type': 'custom',
        'value': 0.0,
        'history': []
    }
```

### Implementing Custom Control Logic
```python
def _implement_control_logic(self):
    # Add your custom control logic here
    if some_condition:
        self.control_actions.append({
            'type': 'custom_control',
            'action': 'custom_action',
            'target': 'target_id'
        })
```

## Troubleshooting

### Common Issues

1. **EPANET toolkit not found**
   ```bash
   pip install epyt
   ```

2. **Network file not found**
   - Ensure the network file path is correct
   - Download EPANET example networks if needed

3. **Import errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

### Getting Help

- Check the test suite: `python test_realtime.py`
- Run individual examples to isolate issues
- Check the console output for specific error messages

## License

This project is part of the HydroTwin water analytics framework.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the test suite
5. Submit a pull request
