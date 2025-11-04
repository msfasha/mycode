"""
SCADA Simulator Module
Simulates sensor readings from EPANET hydraulic simulation with realistic noise
"""
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional


class SCADASimulator:
    """Simulates SCADA sensor readings from EPANET hydraulic simulation"""
    
    def __init__(self, epanet_model):
        """
        Initialize SCADA simulator
        
        Args:
            epanet_model: EPyT epanet model instance
        """
        self.d = epanet_model
        self.sensor_locations = {
            'pressure': [],  # Node indices with pressure sensors
            'flow': [],      # Link indices with flow sensors
            'level': []      # Tank indices with level sensors
        }
        self.noise_levels = {
            'pressure': 0.5,  # meters
            'flow': 2.0,      # LPS
            'level': 0.1      # meters
        }
    
    def add_sensors(self, node_indices: Optional[List[int]] = None, 
                   link_indices: Optional[List[int]] = None, 
                   tank_indices: Optional[List[int]] = None):
        """
        Add virtual sensors at specific locations
        
        Args:
            node_indices: List of node indices for pressure sensors
            link_indices: List of link indices for flow sensors
            tank_indices: List of tank indices for level sensors
        """
        if node_indices:
            self.sensor_locations['pressure'] = node_indices
        if link_indices:
            self.sensor_locations['flow'] = link_indices
        if tank_indices:
            self.sensor_locations['level'] = tank_indices
    
    def auto_deploy_sensors(self, num_pressure: int = 5, num_flow: int = 3):
        """
        Automatically deploy sensors at strategic locations
        
        Args:
            num_pressure: Number of pressure sensors to deploy
            num_flow: Number of flow sensors to deploy
        """
        # Get network size
        num_nodes = self.d.getNodeCount()
        num_links = self.d.getLinkCount()
        
        # Deploy pressure sensors at evenly spaced junctions
        junction_indices = self.d.getNodeJunctionIndex()
        if len(junction_indices) > 0:
            step = max(1, len(junction_indices) // num_pressure)
            self.sensor_locations['pressure'] = junction_indices[::step][:num_pressure]
        
        # Deploy flow sensors at evenly spaced pipes
        pipe_indices = self.d.getLinkPipeIndex()
        if len(pipe_indices) > 0:
            step = max(1, len(pipe_indices) // num_flow)
            self.sensor_locations['flow'] = pipe_indices[::step][:num_flow]
        
        # Deploy level sensors at all tanks
        tank_indices = self.d.getNodeTankIndex()
        self.sensor_locations['level'] = tank_indices
        
        print(f"Auto-deployed sensors:")
        print(f"  - {len(self.sensor_locations['pressure'])} pressure sensors at nodes: {self.sensor_locations['pressure']}")
        print(f"  - {len(self.sensor_locations['flow'])} flow sensors at links: {self.sensor_locations['flow']}")
        print(f"  - {len(self.sensor_locations['level'])} level sensors at tanks: {self.sensor_locations['level']}")
    
    def get_live_data(self, add_noise: bool = True) -> Dict:
        """
        Simulate real-time sensor readings with optional noise
        
        Args:
            add_noise: Whether to add realistic sensor noise
            
        Returns:
            Dictionary containing timestamp and sensor readings
        """
        data = {
            'timestamp': datetime.now(),
            'pressure': {},
            'flow': {},
            'tank_level': {}
        }
        
        # Get pressure readings from junctions
        if self.sensor_locations['pressure']:
            pressures = self.d.getNodePressure()
            node_ids = self.d.getNodeNameID()
            for idx in self.sensor_locations['pressure']:
                value = pressures[idx - 1]
                if add_noise:
                    value += np.random.normal(0, self.noise_levels['pressure'])
                data['pressure'][node_ids[idx - 1]] = max(0, value)  # Pressure can't be negative
        
        # Get flow readings from pipes
        if self.sensor_locations['flow']:
            flows = self.d.getLinkFlows()
            link_ids = self.d.getLinkNameID()
            for idx in self.sensor_locations['flow']:
                value = flows[idx - 1]
                if add_noise:
                    value += np.random.normal(0, self.noise_levels['flow'])
                data['flow'][link_ids[idx - 1]] = value
        
        # Get tank level readings
        if self.sensor_locations['level']:
            tank_indices = self.d.getNodeTankIndex()
            if len(tank_indices) > 0:
                tank_levels = self.d.getNodeTankInitialLevel()
                tank_ids = [self.d.getNodeNameID(idx) for idx in tank_indices]
                for i, idx in enumerate(self.sensor_locations['level']):
                    value = tank_levels[i]
                    if add_noise:
                        value += np.random.normal(0, self.noise_levels['level'])
                    data['tank_level'][tank_ids[i]] = max(0, value)
        
        return data
    
    def get_sensor_summary(self) -> str:
        """Get a summary of deployed sensors"""
        summary = f"SCADA Sensor Deployment Summary\n"
        summary += f"=" * 50 + "\n"
        summary += f"Pressure Sensors: {len(self.sensor_locations['pressure'])} deployed\n"
        summary += f"Flow Sensors: {len(self.sensor_locations['flow'])} deployed\n"
        summary += f"Level Sensors: {len(self.sensor_locations['level'])} deployed\n"
        summary += f"Total Sensors: {sum(len(v) for v in self.sensor_locations.values())}\n"
        return summary
