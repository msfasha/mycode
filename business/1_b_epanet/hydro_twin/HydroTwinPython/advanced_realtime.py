#!/usr/bin/env python3
"""
Advanced Real-time EPANET Simulation with Control Logic
======================================================

This example demonstrates:
1. Real-time monitoring with sensors
2. Control logic implementation
3. Performance tracking
4. Data logging and visualization
5. Alert system

Usage: python advanced_realtime.py
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json
from epyt import epanet

class AdvancedRealTimeSimulator:
    """Advanced real-time simulator with control logic"""
    
    def __init__(self, network_file):
        self.network_file = network_file
        self.d = None
        self.sensors = {}
        self.control_log = []
        self.alerts = []
        self.performance_data = []
        
    def load_network(self):
        """Load and initialize the network"""
        print("Loading network...")
        self.d = epanet(self.network_file)
        
        # Get network components
        self.node_ids = self.d.getNodeNameID()
        self.link_ids = d.getLinkNameID()
        
        print(f"Network loaded: {len(self.node_ids)} nodes, {len(self.link_ids)} links")
        
        # Setup sensors
        self._setup_sensors()
        
    def _setup_sensors(self):
        """Setup virtual sensors for monitoring"""
        # Pressure sensors at junctions
        junction_indices = self.d.getNodeJunctionIndex()
        for i, idx in enumerate(junction_indices[:3]):  # Monitor first 3 junctions
            self.sensors[f'pressure_{i}'] = {
                'type': 'pressure',
                'node_id': self.node_ids[idx],
                'node_index': idx,
                'value': 0.0,
                'history': [],
                'alarm_threshold': 15.0  # Low pressure alarm
            }
        
        # Flow sensors at pipes
        pipe_indices = self.d.getLinkPipeIndex()
        for i, idx in enumerate(pipe_indices[:3]):  # Monitor first 3 pipes
            self.sensors[f'flow_{i}'] = {
                'type': 'flow',
                'link_id': self.link_ids[idx],
                'link_index': idx,
                'value': 0.0,
                'history': [],
                'alarm_threshold': 0.1  # Low flow alarm
            }
        
        # Tank level sensors
        tank_indices = self.d.getNodeTankIndex()
        for i, idx in enumerate(tank_indices):
            self.sensors[f'tank_{i}'] = {
                'type': 'tank_level',
                'node_id': self.node_ids[idx],
                'node_index': idx,
                'value': 0.0,
                'history': [],
                'alarm_threshold': 1.0  # Low tank level alarm
            }
        
        print(f"Setup {len(self.sensors)} sensors")
    
    def read_sensors(self, current_time):
        """Read all sensor values"""
        # Get current simulation results
        pressures = self.d.getNodePressure()
        flows = self.d.getLinkFlows()
        tank_levels = self.d.getNodeTankLevel()
        
        # Update sensor values
        for sensor_id, sensor in self.sensors.items():
            if sensor['type'] == 'pressure':
                sensor['value'] = pressures[sensor['node_index']]
            elif sensor['type'] == 'flow':
                sensor['value'] = flows[sensor['link_index']]
            elif sensor['type'] == 'tank_level':
                sensor['value'] = tank_levels[sensor['node_index']]
            
            # Store history
            sensor['history'].append({
                'time': current_time,
                'value': sensor['value']
            })
    
    def check_alarms(self, current_time):
        """Check for alarm conditions"""
        new_alerts = []
        
        for sensor_id, sensor in self.sensors.items():
            if sensor['value'] < sensor.get('alarm_threshold', 0):
                alert = {
                    'time': current_time,
                    'sensor_id': sensor_id,
                    'sensor_type': sensor['type'],
                    'value': sensor['value'],
                    'threshold': sensor['alarm_threshold'],
                    'message': f"Low {sensor['type']} detected: {sensor['value']:.2f}"
                }
                new_alerts.append(alert)
                self.alerts.append(alert)
        
        return new_alerts
    
    def implement_control_logic(self, current_time):
        """Implement control logic based on sensor readings"""
        control_actions = []
        
        # Example: Pump control based on tank levels
        for sensor_id, sensor in self.sensors.items():
            if sensor['type'] == 'tank_level' and sensor['value'] < 2.0:
                action = {
                    'time': current_time,
                    'type': 'pump_control',
                    'action': 'start_pump',
                    'target': sensor['node_id'],
                    'reason': 'low_tank_level'
                }
                control_actions.append(action)
                self.control_log.append(action)
        
        # Example: Pressure control
        for sensor_id, sensor in self.sensors.items():
            if sensor['type'] == 'pressure' and sensor['value'] < 20.0:
                action = {
                    'time': current_time,
                    'type': 'pressure_control',
                    'action': 'increase_pressure',
                    'target': sensor['node_id'],
                    'reason': 'low_pressure'
                }
                control_actions.append(action)
                self.control_log.append(action)
        
        return control_actions
    
    def calculate_performance_metrics(self, current_time):
        """Calculate system performance metrics"""
        # Calculate averages
        pressure_values = [s['value'] for s in self.sensors.values() if s['type'] == 'pressure']
        flow_values = [s['value'] for s in self.sensors.values() if s['type'] == 'flow']
        tank_values = [s['value'] for s in self.sensors.values() if s['type'] == 'tank_level']
        
        metrics = {
            'time': current_time,
            'avg_pressure': np.mean(pressure_values) if pressure_values else 0,
            'min_pressure': np.min(pressure_values) if pressure_values else 0,
            'max_pressure': np.max(pressure_values) if pressure_values else 0,
            'total_flow': np.sum(np.abs(flow_values)) if flow_values else 0,
            'avg_tank_level': np.mean(tank_values) if tank_values else 0,
            'num_alerts': len([a for a in self.alerts if a['time'] == current_time]),
            'num_controls': len([c for c in self.control_log if c['time'] == current_time])
        }
        
        self.performance_data.append(metrics)
        return metrics
    
    def run_simulation(self, duration_hours=24):
        """Run the real-time simulation"""
        print(f"\nStarting advanced real-time simulation for {duration_hours} hours")
        print("=" * 60)
        
        # Initialize hydraulic analysis
        self.d.openHydraulicAnalysis()
        self.d.initializeHydraulicAnalysis()
        
        time_step = 3600  # 1 hour
        total_time = duration_hours * 3600
        current_time = 0
        
        start_time = time.time()
        
        try:
            while current_time < total_time:
                # Run hydraulic analysis
                self.d.runHydraulicAnalysis()
                
                # Read sensors
                self.read_sensors(current_time)
                
                # Check alarms
                new_alerts = self.check_alarms(current_time)
                
                # Implement control logic
                control_actions = self.implement_control_logic(current_time)
                
                # Calculate performance metrics
                metrics = self.calculate_performance_metrics(current_time)
                
                # Print status
                if current_time % 3600 == 0:  # Every hour
                    hour = current_time / 3600
                    print(f"Time: {hour:2.0f}h - "
                          f"Avg Pressure: {metrics['avg_pressure']:6.2f} m - "
                          f"Total Flow: {metrics['total_flow']:8.2f} L/s - "
                          f"Alerts: {metrics['num_alerts']} - "
                          f"Controls: {metrics['num_controls']}")
                    
                    # Print new alerts
                    for alert in new_alerts:
                        print(f"  ALERT: {alert['message']}")
                    
                    # Print control actions
                    for action in control_actions:
                        print(f"  CONTROL: {action['action']} for {action['target']}")
                
                # Advance time
                current_time += time_step
                
                # Simulate real-time delay
                time.sleep(0.1)
        
        except Exception as e:
            print(f"Simulation error: {e}")
        
        finally:
            self.d.closeHydraulicAnalysis()
            self.d.unload()
        
        elapsed_time = time.time() - start_time
        print(f"\nSimulation completed in {elapsed_time:.2f} seconds")
    
    def generate_report(self):
        """Generate simulation report"""
        report = {
            'simulation_summary': {
                'total_alerts': len(self.alerts),
                'total_controls': len(self.control_log),
                'sensors': len(self.sensors),
                'performance_points': len(self.performance_data)
            },
            'alerts_summary': {
                'by_type': {},
                'by_time': {}
            },
            'control_summary': {
                'by_type': {},
                'by_time': {}
            },
            'performance_summary': self._calculate_performance_summary()
        }
        
        # Analyze alerts by type
        for alert in self.alerts:
            alert_type = alert['sensor_type']
            report['alerts_summary']['by_type'][alert_type] = \
                report['alerts_summary']['by_type'].get(alert_type, 0) + 1
        
        # Analyze controls by type
        for control in self.control_log:
            control_type = control['type']
            report['control_summary']['by_type'][control_type] = \
                report['control_summary']['by_type'].get(control_type, 0) + 1
        
        return report
    
    def _calculate_performance_summary(self):
        """Calculate performance summary statistics"""
        if not self.performance_data:
            return {}
        
        pressures = [p['avg_pressure'] for p in self.performance_data]
        flows = [p['total_flow'] for p in self.performance_data]
        tank_levels = [p['avg_tank_level'] for p in self.performance_data]
        
        return {
            'pressure': {
                'mean': np.mean(pressures),
                'min': np.min(pressures),
                'max': np.max(pressures),
                'std': np.std(pressures)
            },
            'flow': {
                'mean': np.mean(flows),
                'min': np.min(flows),
                'max': np.max(flows),
                'std': np.std(flows)
            },
            'tank_level': {
                'mean': np.mean(tank_levels),
                'min': np.min(tank_levels),
                'max': np.max(tank_levels),
                'std': np.std(tank_levels)
            }
        }
    
    def plot_results(self):
        """Plot simulation results"""
        if not self.performance_data:
            print("No data to plot")
            return
        
        # Extract data
        times = [p['time'] / 3600 for p in self.performance_data]  # Convert to hours
        pressures = [p['avg_pressure'] for p in self.performance_data]
        flows = [p['total_flow'] for p in self.performance_data]
        tank_levels = [p['avg_tank_level'] for p in self.performance_data]
        
        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Pressure plot
        axes[0, 0].plot(times, pressures, 'b-', linewidth=2)
        axes[0, 0].set_ylabel('Average Pressure (m)')
        axes[0, 0].set_title('System Pressure Over Time')
        axes[0, 0].grid(True)
        
        # Flow plot
        axes[0, 1].plot(times, flows, 'g-', linewidth=2)
        axes[0, 1].set_ylabel('Total Flow (L/s)')
        axes[0, 1].set_title('System Flow Over Time')
        axes[0, 1].grid(True)
        
        # Tank level plot
        axes[1, 0].plot(times, tank_levels, 'r-', linewidth=2)
        axes[1, 0].set_ylabel('Average Tank Level (m)')
        axes[1, 0].set_xlabel('Time (hours)')
        axes[1, 0].set_title('Tank Levels Over Time')
        axes[1, 0].grid(True)
        
        # Alerts and controls over time
        alert_times = [a['time'] / 3600 for a in self.alerts]
        control_times = [c['time'] / 3600 for c in self.control_log]
        
        axes[1, 1].hist(alert_times, bins=24, alpha=0.7, label='Alerts', color='red')
        axes[1, 1].hist(control_times, bins=24, alpha=0.7, label='Controls', color='blue')
        axes[1, 1].set_xlabel('Time (hours)')
        axes[1, 1].set_ylabel('Count')
        axes[1, 1].set_title('Alerts and Controls Over Time')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig('advanced_realtime_results.png', dpi=300, bbox_inches='tight')
        print("Plots saved as 'advanced_realtime_results.png'")
        plt.show()
    
    def save_data(self, filename='advanced_realtime_data.json'):
        """Save simulation data"""
        data = {
            'report': self.generate_report(),
            'sensors': self.sensors,
            'alerts': self.alerts,
            'controls': self.control_log,
            'performance': self.performance_data
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Data saved to {filename}")


def main():
    """Main function"""
    network_file = "water-networks/Net1.inp"
    
    print("Advanced Real-time EPANET Simulation")
    print("=" * 50)
    
    try:
        # Create simulator
        simulator = AdvancedRealTimeSimulator(network_file)
        
        # Load network
        simulator.load_network()
        
        # Run simulation
        simulator.run_simulation(duration_hours=24)
        
        # Generate report
        report = simulator.generate_report()
        print("\n" + "="*50)
        print("SIMULATION REPORT")
        print("="*50)
        print(json.dumps(report, indent=2, default=str))
        
        # Plot results
        simulator.plot_results()
        
        # Save data
        simulator.save_data()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
