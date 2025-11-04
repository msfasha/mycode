#!/usr/bin/env python3
"""
SCADA Integration Example for Real-time EPANET Simulation
=========================================================

This example demonstrates how to integrate real-time EPANET simulation
with SCADA systems and real-time data sources.

Features:
- Simulated SCADA data sources
- Real-time data integration
- Database logging
- Web API for monitoring
- Alert system
- Control system integration

Usage: python scada_integration.py
"""

import time
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
from epyt import epanet

class SCADADataSource:
    """Simulated SCADA data source"""
    
    def __init__(self, sensor_config: Dict[str, Any]):
        self.sensor_config = sensor_config
        self.data_buffer = {}
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the SCADA data source"""
        self.running = True
        self.thread = threading.Thread(target=self._generate_data)
        self.thread.start()
        print("SCADA data source started")
    
    def stop(self):
        """Stop the SCADA data source"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("SCADA data source stopped")
    
    def _generate_data(self):
        """Generate simulated SCADA data"""
        while self.running:
            current_time = datetime.now()
            
            for sensor_id, config in self.sensor_config.items():
                # Generate realistic sensor data
                base_value = config.get('base_value', 0)
                noise_level = config.get('noise_level', 0.1)
                trend = config.get('trend', 0)
                
                # Add some realistic variation
                noise = np.random.normal(0, noise_level)
                trend_value = trend * (current_time.hour / 24.0)
                value = base_value + noise + trend_value
                
                # Store in buffer
                self.data_buffer[sensor_id] = {
                    'timestamp': current_time,
                    'value': value,
                    'quality': 'good' if abs(noise) < noise_level * 2 else 'poor'
                }
            
            time.sleep(1)  # Update every second
    
    def get_data(self, sensor_id: str) -> Dict[str, Any]:
        """Get latest data for a sensor"""
        return self.data_buffer.get(sensor_id, {})
    
    def get_all_data(self) -> Dict[str, Any]:
        """Get all sensor data"""
        return self.data_buffer.copy()

class DatabaseLogger:
    """Database logger for simulation data"""
    
    def __init__(self, db_file: str = "realtime_simulation.db"):
        self.db_file = db_file
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                sensor_id TEXT,
                value REAL,
                quality TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                avg_pressure REAL,
                total_flow REAL,
                avg_tank_level REAL,
                num_alerts INTEGER,
                num_controls INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                sensor_id TEXT,
                alert_type TEXT,
                message TEXT,
                value REAL,
                threshold REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS controls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                control_type TEXT,
                action TEXT,
                target TEXT,
                reason TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_sensor_data(self, sensor_id: str, value: float, quality: str):
        """Log sensor data to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_data (timestamp, sensor_id, value, quality)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now(), sensor_id, value, quality))
        
        conn.commit()
        conn.close()
    
    def log_simulation_results(self, results: Dict[str, Any]):
        """Log simulation results to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO simulation_results 
            (timestamp, avg_pressure, total_flow, avg_tank_level, num_alerts, num_controls)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now(),
            results.get('avg_pressure', 0),
            results.get('total_flow', 0),
            results.get('avg_tank_level', 0),
            results.get('num_alerts', 0),
            results.get('num_controls', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def log_alert(self, sensor_id: str, alert_type: str, message: str, 
                  value: float, threshold: float):
        """Log alert to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (timestamp, sensor_id, alert_type, 
                               message, value, threshold)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now(), sensor_id, alert_type, message, value, threshold))
        
        conn.commit()
        conn.close()
    
    def log_control(self, control_type: str, action: str, target: str, reason: str):
        """Log control action to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO controls (timestamp, control_type, action, target, reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now(), control_type, action, target, reason))
        
        conn.commit()
        conn.close()

class SCADAIntegratedSimulator:
    """Real-time simulator with SCADA integration"""
    
    def __init__(self, network_file: str):
        self.network_file = network_file
        self.d = None
        self.scada_source = None
        self.db_logger = None
        self.sensors = {}
        self.alerts = []
        self.controls = []
        self.performance_data = []
        
        # Initialize components
        self._load_network()
        self._setup_scada()
        self._setup_database()
    
    def _load_network(self):
        """Load EPANET network"""
        print("Loading network...")
        self.d = epanet(self.network_file)
        
        # Get network info
        self.node_ids = self.d.getNodeNameID()
        self.link_ids = self.d.getLinkNameID()
        
        print(f"Network loaded: {len(self.node_ids)} nodes, {len(self.link_ids)} links")
    
    def _setup_scada(self):
        """Setup SCADA data source"""
        # Configure sensors
        sensor_config = {
            'pressure_1': {'base_value': 25.0, 'noise_level': 1.0, 'trend': -0.5},
            'pressure_2': {'base_value': 30.0, 'noise_level': 1.2, 'trend': 0.3},
            'flow_1': {'base_value': 50.0, 'noise_level': 5.0, 'trend': 2.0},
            'flow_2': {'base_value': 75.0, 'noise_level': 3.0, 'trend': -1.0},
            'tank_level_1': {'base_value': 5.0, 'noise_level': 0.2, 'trend': 0.1}
        }
        
        self.scada_source = SCADADataSource(sensor_config)
        self.scada_source.start()
        
        print("SCADA data source configured and started")
    
    def _setup_database(self):
        """Setup database logger"""
        self.db_logger = DatabaseLogger()
        print("Database logger initialized")
    
    def _read_scada_data(self):
        """Read data from SCADA system"""
        scada_data = self.scada_source.get_all_data()
        
        for sensor_id, data in scada_data.items():
            if sensor_id not in self.sensors:
                self.sensors[sensor_id] = {
                    'type': self._get_sensor_type(sensor_id),
                    'value': 0.0,
                    'quality': 'good',
                    'history': []
                }
            
            self.sensors[sensor_id]['value'] = data['value']
            self.sensors[sensor_id]['quality'] = data['quality']
            self.sensors[sensor_id]['history'].append({
                'timestamp': data['timestamp'],
                'value': data['value']
            })
            
            # Log to database
            self.db_logger.log_sensor_data(sensor_id, data['value'], data['quality'])
    
    def _get_sensor_type(self, sensor_id: str) -> str:
        """Determine sensor type from ID"""
        if 'pressure' in sensor_id:
            return 'pressure'
        elif 'flow' in sensor_id:
            return 'flow'
        elif 'tank' in sensor_id:
            return 'tank_level'
        else:
            return 'unknown'
    
    def _check_alarms(self):
        """Check for alarm conditions"""
        new_alerts = []
        
        for sensor_id, sensor in self.sensors.items():
            if sensor['type'] == 'pressure' and sensor['value'] < 20.0:
                alert = {
                    'sensor_id': sensor_id,
                    'type': 'low_pressure',
                    'message': f"Low pressure detected: {sensor['value']:.2f}",
                    'value': sensor['value'],
                    'threshold': 20.0
                }
                new_alerts.append(alert)
                self.alerts.append(alert)
                
                # Log to database
                self.db_logger.log_alert(
                    sensor_id, 'low_pressure', alert['message'],
                    sensor['value'], 20.0
                )
            
            elif sensor['type'] == 'tank_level' and sensor['value'] < 2.0:
                alert = {
                    'sensor_id': sensor_id,
                    'type': 'low_tank_level',
                    'message': f"Low tank level detected: {sensor['value']:.2f}",
                    'value': sensor['value'],
                    'threshold': 2.0
                }
                new_alerts.append(alert)
                self.alerts.append(alert)
                
                # Log to database
                self.db_logger.log_alert(
                    sensor_id, 'low_tank_level', alert['message'],
                    sensor['value'], 2.0
                )
        
        return new_alerts
    
    def _implement_controls(self):
        """Implement control logic based on SCADA data"""
        control_actions = []
        
        for sensor_id, sensor in self.sensors.items():
            if sensor['type'] == 'tank_level' and sensor['value'] < 2.0:
                action = {
                    'type': 'pump_control',
                    'action': 'start_pump',
                    'target': sensor_id,
                    'reason': 'low_tank_level'
                }
                control_actions.append(action)
                self.controls.append(action)
                
                # Log to database
                self.db_logger.log_control(
                    'pump_control', 'start_pump', sensor_id, 'low_tank_level'
                )
            
            elif sensor['type'] == 'pressure' and sensor['value'] < 20.0:
                action = {
                    'type': 'pressure_control',
                    'action': 'increase_pressure',
                    'target': sensor_id,
                    'reason': 'low_pressure'
                }
                control_actions.append(action)
                self.controls.append(action)
                
                # Log to database
                self.db_logger.log_control(
                    'pressure_control', 'increase_pressure', sensor_id, 'low_pressure'
                )
        
        return control_actions
    
    def _calculate_performance_metrics(self):
        """Calculate system performance metrics"""
        pressure_values = [s['value'] for s in self.sensors.values() if s['type'] == 'pressure']
        flow_values = [s['value'] for s in self.sensors.values() if s['type'] == 'flow']
        tank_values = [s['value'] for s in self.sensors.values() if s['type'] == 'tank_level']
        
        metrics = {
            'timestamp': datetime.now(),
            'avg_pressure': np.mean(pressure_values) if pressure_values else 0,
            'total_flow': np.sum(np.abs(flow_values)) if flow_values else 0,
            'avg_tank_level': np.mean(tank_values) if tank_values else 0,
            'num_alerts': len([a for a in self.alerts if (datetime.now() - a.get('timestamp', datetime.now())).seconds < 3600]),
            'num_controls': len([c for c in self.controls if (datetime.now() - c.get('timestamp', datetime.now())).seconds < 3600])
        }
        
        self.performance_data.append(metrics)
        
        # Log to database
        self.db_logger.log_simulation_results(metrics)
        
        return metrics
    
    def run_simulation(self, duration_minutes: int = 60):
        """Run the SCADA-integrated simulation"""
        print(f"\nStarting SCADA-integrated simulation for {duration_minutes} minutes")
        print("=" * 60)
        
        # Initialize hydraulic analysis
        self.d.openHydraulicAnalysis()
        self.d.initializeHydraulicAnalysis()
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                # Run hydraulic analysis
                self.d.runHydraulicAnalysis()
                
                # Read SCADA data
                self._read_scada_data()
                
                # Check alarms
                new_alerts = self._check_alarms()
                
                # Implement controls
                control_actions = self._implement_controls()
                
                # Calculate performance metrics
                metrics = self._calculate_performance_metrics()
                
                # Print status
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"[{current_time}] "
                      f"Pressure: {metrics['avg_pressure']:.2f} m - "
                      f"Flow: {metrics['total_flow']:.2f} L/s - "
                      f"Alerts: {metrics['num_alerts']} - "
                      f"Controls: {metrics['num_controls']}")
                
                # Print new alerts
                for alert in new_alerts:
                    print(f"  ALERT: {alert['message']}")
                
                # Print control actions
                for action in control_actions:
                    print(f"  CONTROL: {action['action']} for {action['target']}")
                
                # Wait for next iteration
                time.sleep(5)  # 5-second intervals
        
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        
        except Exception as e:
            print(f"Simulation error: {e}")
        
        finally:
            # Cleanup
            self.d.closeHydraulicAnalysis()
            self.d.unload()
            self.scada_source.stop()
            
            elapsed_time = time.time() - start_time
            print(f"\nSimulation completed in {elapsed_time:.2f} seconds")
    
    def generate_report(self):
        """Generate simulation report"""
        report = {
            'simulation_summary': {
                'duration_minutes': len(self.performance_data),
                'total_alerts': len(self.alerts),
                'total_controls': len(self.controls),
                'sensors': len(self.sensors)
            },
            'performance_summary': self._calculate_summary_metrics(),
            'database_file': 'realtime_simulation.db'
        }
        
        return report
    
    def _calculate_summary_metrics(self):
        """Calculate summary performance metrics"""
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

def main():
    """Main function"""
    network_file = "water-networks/Net1.inp"
    
    print("SCADA-Integrated Real-time EPANET Simulation")
    print("=" * 50)
    
    try:
        # Create simulator
        simulator = SCADAIntegratedSimulator(network_file)
        
        # Run simulation
        simulator.run_simulation(duration_minutes=10)  # 10-minute simulation
        
        # Generate report
        report = simulator.generate_report()
        print("\n" + "="*50)
        print("SIMULATION REPORT")
        print("="*50)
        print(json.dumps(report, indent=2, default=str))
        
        print(f"\nDatabase file: realtime_simulation.db")
        print("You can query the database to analyze the simulation data.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
