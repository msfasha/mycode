"""SCADA data simulator service."""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
from services.time_patterns import get_diurnal_multiplier, generate_time_range
from config import PRESSURE_NOISE_PERCENT, FLOW_NOISE_PERCENT, LEVEL_NOISE_PERCENT


class SCADASimulator:
    """Generates realistic SCADA sensor data from baseline."""
    
    def __init__(self, baseline_data: Dict):
        """Initialize with baseline data."""
        self.baseline_pressures = baseline_data.get('pressures', {})
        self.baseline_flows = baseline_data.get('flows', {})
        self.baseline_tank_levels = baseline_data.get('tank_levels', {})
    
    def generate_sensor_data(
        self,
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int = 1
    ) -> List[Dict]:
        """
        Generate SCADA sensor readings for time period.
        
        Returns list of sensor readings with:
        - timestamp
        - sensor_id
        - sensor_type (pressure, flow, level)
        - value
        - location_id
        """
        sensor_readings = []
        
        for current_time in generate_time_range(start_time, end_time, interval_minutes):
            # Get time-of-day multiplier
            hour = current_time.hour + current_time.minute / 60.0
            multiplier = get_diurnal_multiplier(hour)
            
            # Generate pressure sensor readings
            for node_id, baseline_pressure in self.baseline_pressures.items():
                # Apply diurnal pattern (pressure varies inversely with demand)
                pressure = baseline_pressure * (1.0 - (multiplier - 1.0) * 0.3)
                
                # Add noise
                noise = np.random.normal(0, PRESSURE_NOISE_PERCENT / 100.0)
                pressure = pressure * (1.0 + noise)
                
                sensor_readings.append({
                    'timestamp': current_time,
                    'sensor_id': f'PRESSURE_{node_id}',
                    'sensor_type': 'pressure',
                    'value': float(pressure),
                    'location_id': node_id
                })
            
            # Generate flow sensor readings
            for link_id, baseline_flow in self.baseline_flows.items():
                # Flow varies directly with demand pattern
                flow = baseline_flow * multiplier
                
                # Add noise
                noise = np.random.normal(0, FLOW_NOISE_PERCENT / 100.0)
                flow = flow * (1.0 + noise)
                
                sensor_readings.append({
                    'timestamp': current_time,
                    'sensor_id': f'FLOW_{link_id}',
                    'sensor_type': 'flow',
                    'value': float(flow),
                    'location_id': link_id
                })
            
            # Generate tank level readings
            for tank_id, baseline_level in self.baseline_tank_levels.items():
                # Tank levels change slowly, influenced by time of day
                level = baseline_level * (1.0 + (multiplier - 1.0) * 0.05)
                
                # Add noise
                noise = np.random.normal(0, LEVEL_NOISE_PERCENT / 100.0)
                level = level * (1.0 + noise)
                
                sensor_readings.append({
                    'timestamp': current_time,
                    'sensor_id': f'LEVEL_{tank_id}',
                    'sensor_type': 'level',
                    'value': float(level),
                    'location_id': tank_id
                })
        
        return sensor_readings
    
    def get_sensor_list(self) -> List[Dict]:
        """Get list of all available sensors."""
        sensors = []
        
        # Pressure sensors
        for node_id in self.baseline_pressures.keys():
            sensors.append({
                'sensor_id': f'PRESSURE_{node_id}',
                'sensor_type': 'pressure',
                'location_id': node_id,
                'location_name': node_id
            })
        
        # Flow sensors
        for link_id in self.baseline_flows.keys():
            sensors.append({
                'sensor_id': f'FLOW_{link_id}',
                'sensor_type': 'flow',
                'location_id': link_id,
                'location_name': link_id
            })
        
        # Level sensors
        for tank_id in self.baseline_tank_levels.keys():
            sensors.append({
                'sensor_id': f'LEVEL_{tank_id}',
                'sensor_type': 'level',
                'location_id': tank_id,
                'location_name': tank_id
            })
        
        return sensors



