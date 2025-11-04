#!/usr/bin/env python3
"""
Real-time EPANET Simulation Example
====================================

This script demonstrates how to perform real-time simulation of a water distribution network
using the EPyT library. It simulates real-time conditions by:

1. Loading a network model
2. Running step-by-step hydraulic simulations
3. Simulating real-time sensor data
4. Implementing control logic
5. Monitoring system performance

Author: Generated for EPANET real-time simulation
Date: 2024
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os
from epyt import epanet

class RealTimeSimulator:
    """
    Real-time EPANET simulation class that handles:
    - Network loading and initialization
    - Step-by-step hydraulic simulation
    - Real-time data monitoring
    - Control logic implementation
    - Performance tracking
    """
    
    def __init__(self, network_file, simulation_duration_hours=24):
        """
        Initialize the real-time simulator
        
        Args:
            network_file (str): Path to EPANET .inp file
            simulation_duration_hours (int): Duration of simulation in hours
        """
        self.network_file = network_file
        self.simulation_duration = simulation_duration_hours * 3600  # Convert to seconds
        self.d = None
        self.current_time = 0
        self.time_step = 3600  # 1 hour time step
        self.sensor_data = {}
        self.control_log = []
        self.performance_metrics = {}
        
        # Initialize the network
        self._load_network()
        self._setup_sensors()
        
    def _load_network(self):
        """Load the EPANET network model"""
        try:
            print(f"Loading network: {self.network_file}")
            self.d = epanet(self.network_file)
            
            # Get network information
            self.network_info = {
                'nodes': self.d.getNodeCount(),
                'links': self.d.getLinkCount(),
                'junctions': self.d.getNodeJunctionCount(),
                'tanks': self.d.getNodeTankCount(),
                'reservoirs': self.d.getNodeReservoirCount(),
                'pipes': self.d.getLinkPipeCount(),
                'pumps': self.d.getLinkPumpCount(),
                'valves': self.d.getLinkValveCount()
            }
            
            print("Network loaded successfully!")
            print(f"Network components: {self.network_info}")
            
        except Exception as e:
            print(f"Error loading network: {e}")
            raise
    
    def _setup_sensors(self):
        """Setup virtual sensors for monitoring key parameters"""
        # Get node and link IDs
        self.node_ids = self.d.getNodeNameID()
        self.link_ids = self.d.getLinkNameID()
        
        # Setup pressure sensors at junctions
        self.pressure_sensors = []
        junction_indices = self.d.getNodeJunctionIndex()
        for i, idx in enumerate(junction_indices[:5]):  # Monitor first 5 junctions
            self.pressure_sensors.append({
                'node_id': self.node_ids[idx],
                'node_index': idx,
                'type': 'pressure',
                'current_value': 0.0,
                'history': []
            })
        
        # Setup flow sensors at pipes
        self.flow_sensors = []
        pipe_indices = self.d.getLinkPipeIndex()
        for i, idx in enumerate(pipe_indices[:5]):  # Monitor first 5 pipes
            self.flow_sensors.append({
                'link_id': self.link_ids[idx],
                'link_index': idx,
                'type': 'flow',
                'current_value': 0.0,
                'history': []
            })
        
        # Setup tank level sensors
        self.tank_sensors = []
        tank_indices = self.d.getNodeTankIndex()
        for idx in tank_indices:
            self.tank_sensors.append({
                'node_id': self.node_ids[idx],
                'node_index': idx,
                'type': 'tank_level',
                'current_value': 0.0,
                'history': []
            })
        
        print(f"Setup {len(self.pressure_sensors)} pressure sensors")
        print(f"Setup {len(self.flow_sensors)} flow sensors")
        print(f"Setup {len(self.tank_sensors)} tank level sensors")
    
    def _read_sensor_data(self):
        """Read current sensor values from the simulation"""
        # Read pressure data
        pressures = self.d.getNodePressure()
        for sensor in self.pressure_sensors:
            sensor['current_value'] = pressures[sensor['node_index']]
            sensor['history'].append({
                'time': self.current_time,
                'value': sensor['current_value']
            })
        
        # Read flow data
        flows = self.d.getLinkFlows()
        for sensor in self.flow_sensors:
            sensor['current_value'] = flows[sensor['link_index']]
            sensor['history'].append({
                'time': self.current_time,
                'value': sensor['current_value']
            })
        
        # Read tank level data
        tank_levels = self.d.getNodeTankLevel()
        for sensor in self.tank_sensors:
            sensor['current_value'] = tank_levels[sensor['node_index']]
            sensor['history'].append({
                'time': self.current_time,
                'value': sensor['current_value']
            })
    
    def _implement_control_logic(self):
        """Implement real-time control logic based on sensor readings"""
        control_actions = []
        
        # Example: Tank level control
        for sensor in self.tank_sensors:
            if sensor['current_value'] < 2.0:  # Low tank level
                control_actions.append({
                    'type': 'pump_control',
                    'action': 'start_pump',
                    'target': sensor['node_id'],
                    'reason': 'low_tank_level'
                })
            elif sensor['current_value'] > 8.0:  # High tank level
                control_actions.append({
                    'type': 'pump_control',
                    'action': 'stop_pump',
                    'target': sensor['node_id'],
                    'reason': 'high_tank_level'
                })
        
        # Example: Pressure control
        for sensor in self.pressure_sensors:
            if sensor['current_value'] < 20.0:  # Low pressure
                control_actions.append({
                    'type': 'pressure_control',
                    'action': 'increase_pressure',
                    'target': sensor['node_id'],
                    'reason': 'low_pressure'
                })
        
        # Log control actions
        if control_actions:
            self.control_log.extend(control_actions)
            print(f"Control actions at time {self.current_time}: {len(control_actions)} actions")
            for action in control_actions:
                print(f"  - {action['type']}: {action['action']} for {action['target']}")
        
        return control_actions
    
    def _calculate_performance_metrics(self):
        """Calculate system performance metrics"""
        # Calculate average pressure
        pressures = [sensor['current_value'] for sensor in self.pressure_sensors]
        avg_pressure = np.mean(pressures) if pressures else 0
        
        # Calculate total flow
        flows = [abs(sensor['current_value']) for sensor in self.flow_sensors]
        total_flow = np.sum(flows) if flows else 0
        
        # Calculate tank levels
        tank_levels = [sensor['current_value'] for sensor in self.tank_sensors]
        avg_tank_level = np.mean(tank_levels) if tank_levels else 0
        
        # Store metrics
        self.performance_metrics[self.current_time] = {
            'avg_pressure': avg_pressure,
            'total_flow': total_flow,
            'avg_tank_level': avg_tank_level,
            'pressure_sensors': len(self.pressure_sensors),
            'flow_sensors': len(self.flow_sensors),
            'tank_sensors': len(self.tank_sensors)
        }
    
    def run_simulation(self):
        """Run the real-time simulation"""
        print(f"\nStarting real-time simulation for {self.simulation_duration/3600:.1f} hours")
        print("=" * 60)
        
        # Initialize hydraulic analysis
        self.d.openHydraulicAnalysis()
        self.d.initializeHydraulicAnalysis()
        
        start_time = time.time()
        
        try:
            while self.current_time < self.simulation_duration:
                # Run hydraulic analysis for current time step
                self.d.runHydraulicAnalysis()
                
                # Read sensor data
                self._read_sensor_data()
                
                # Implement control logic
                control_actions = self._implement_control_logic()
                
                # Calculate performance metrics
                self._calculate_performance_metrics()
                
                # Print status
                if self.current_time % 3600 == 0:  # Every hour
                    hour = self.current_time / 3600
                    print(f"Time: {hour:.1f}h - "
                          f"Avg Pressure: {self.performance_metrics[self.current_time]['avg_pressure']:.2f} m - "
                          f"Total Flow: {self.performance_metrics[self.current_time]['total_flow']:.2f} L/s")
                
                # Advance to next time step
                self.current_time += self.time_step
                
                # Simulate real-time delay (remove in actual implementation)
                time.sleep(0.1)  # 100ms delay to simulate real-time processing
                
        except Exception as e:
            print(f"Simulation error at time {self.current_time}: {e}")
        
        finally:
            # Close analysis
            self.d.closeHydraulicAnalysis()
            
        elapsed_time = time.time() - start_time
        print(f"\nSimulation completed in {elapsed_time:.2f} seconds")
        print(f"Simulated {self.simulation_duration/3600:.1f} hours in real-time")
    
    def generate_report(self):
        """Generate a comprehensive simulation report"""
        report = {
            'simulation_info': {
                'network_file': self.network_file,
                'duration_hours': self.simulation_duration / 3600,
                'time_step_seconds': self.time_step,
                'total_steps': int(self.simulation_duration / self.time_step)
            },
            'network_info': self.network_info,
            'sensor_summary': {
                'pressure_sensors': len(self.pressure_sensors),
                'flow_sensors': len(self.flow_sensors),
                'tank_sensors': len(self.tank_sensors)
            },
            'control_actions': len(self.control_log),
            'performance_summary': self._calculate_summary_metrics()
        }
        
        return report
    
    def _calculate_summary_metrics(self):
        """Calculate summary performance metrics"""
        if not self.performance_metrics:
            return {}
        
        pressures = [metrics['avg_pressure'] for metrics in self.performance_metrics.values()]
        flows = [metrics['total_flow'] for metrics in self.performance_metrics.values()]
        tank_levels = [metrics['avg_tank_level'] for metrics in self.performance_metrics.values()]
        
        return {
            'avg_pressure': {
                'mean': np.mean(pressures),
                'min': np.min(pressures),
                'max': np.max(pressures),
                'std': np.std(pressures)
            },
            'total_flow': {
                'mean': np.mean(flows),
                'min': np.min(flows),
                'max': np.max(flows),
                'std': np.std(flows)
            },
            'avg_tank_level': {
                'mean': np.mean(tank_levels),
                'min': np.min(tank_levels),
                'max': np.max(tank_levels),
                'std': np.std(tank_levels)
            }
        }
    
    def plot_results(self, save_plots=True):
        """Plot simulation results"""
        if not self.performance_metrics:
            print("No data to plot")
            return
        
        # Extract time series data
        times = list(self.performance_metrics.keys())
        pressures = [self.performance_metrics[t]['avg_pressure'] for t in times]
        flows = [self.performance_metrics[t]['total_flow'] for t in times]
        tank_levels = [self.performance_metrics[t]['avg_tank_level'] for t in times]
        
        # Convert time to hours
        time_hours = [t / 3600 for t in times]
        
        # Create plots
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # Pressure plot
        axes[0].plot(time_hours, pressures, 'b-', linewidth=2)
        axes[0].set_ylabel('Average Pressure (m)')
        axes[0].set_title('Real-time Simulation Results')
        axes[0].grid(True)
        
        # Flow plot
        axes[1].plot(time_hours, flows, 'g-', linewidth=2)
        axes[1].set_ylabel('Total Flow (L/s)')
        axes[1].grid(True)
        
        # Tank level plot
        axes[2].plot(time_hours, tank_levels, 'r-', linewidth=2)
        axes[2].set_ylabel('Average Tank Level (m)')
        axes[2].set_xlabel('Time (hours)')
        axes[2].grid(True)
        
        plt.tight_layout()
        
        if save_plots:
            plt.savefig('realtime_simulation_results.png', dpi=300, bbox_inches='tight')
            print("Plots saved as 'realtime_simulation_results.png'")
        
        plt.show()
    
    def save_data(self, filename='realtime_simulation_data.json'):
        """Save simulation data to JSON file"""
        data = {
            'simulation_report': self.generate_report(),
            'sensor_data': {
                'pressure_sensors': self.pressure_sensors,
                'flow_sensors': self.flow_sensors,
                'tank_sensors': self.tank_sensors
            },
            'control_log': self.control_log,
            'performance_metrics': self.performance_metrics
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Simulation data saved to {filename}")


def main():
    """Main function to run the real-time simulation"""
    # Network file path (adjust as needed)
    network_file = "water-networks/Net1.inp"
    
    # Check if network file exists
    if not os.path.exists(network_file):
        print(f"Network file not found: {network_file}")
        print("Please ensure the network file exists or update the path")
        return
    
    try:
        # Create simulator
        simulator = RealTimeSimulator(network_file, simulation_duration_hours=24)
        
        # Run simulation
        simulator.run_simulation()
        
        # Generate report
        report = simulator.generate_report()
        print("\n" + "="*60)
        print("SIMULATION REPORT")
        print("="*60)
        print(json.dumps(report, indent=2, default=str))
        
        # Plot results
        simulator.plot_results()
        
        # Save data
        simulator.save_data()
        
    except Exception as e:
        print(f"Error running simulation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
