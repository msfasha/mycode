"""Service for loading EPANET network files."""
from pathlib import Path
from typing import Dict, List
from epyt import epanet
import numpy as np


class NetworkLoader:
    """Loads and parses EPANET .inp files."""
    
    def __init__(self, file_path: str):
        """Initialize with network file path."""
        self.file_path = Path(file_path)
        self.d = None
    
    def load(self):
        """Load the network file using EPyT."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Network file not found: {self.file_path}")
        
        self.d = epanet(str(self.file_path))
        return self
    
    def get_network_info(self) -> Dict:
        """Extract network information."""
        if not self.d:
            self.load()
        
        # Get basic info
        node_names = self.d.getNodeNameID()
        node_types = self.d.getNodeType()
        link_names = self.d.getLinkNameID()
        link_types = self.d.getLinkType()
        
        # Get coordinates if available
        try:
            coordinates = self.d.getNodeCoordinates()
            coords_dict = {}
            if isinstance(coordinates, dict) and 'x' in coordinates:
                for i, node_id in enumerate(node_names):
                    if i < len(coordinates['x']) and i < len(coordinates['y']):
                        coords_dict[node_id] = {
                            'x': coordinates['x'][i],
                            'y': coordinates['y'][i]
                        }
        except:
            coords_dict = {}
        
        # Extract junctions
        junctions = []
        for i, (node_id, node_type) in enumerate(zip(node_names, node_types)):
            if node_type == 'JUNCTION':
                elevation = self.d.getNodeElevations()[i] if hasattr(self.d, 'getNodeElevations') else 0
                demands = self.d.getNodeBaseDemands()
                demand = demands[1][i] if 1 in demands else 0
                
                coords = coords_dict.get(node_id, {})
                junctions.append({
                    'id': node_id,
                    'elevation': float(elevation),
                    'demand': float(demand),
                    'x': coords.get('x'),
                    'y': coords.get('y')
                })
        
        # Extract pipes
        pipes = []
        for i, (link_id, link_type) in enumerate(zip(link_names, link_types)):
            if link_type == 'PIPE':
                # Get node connections
                link_nodes = self.d.getLinkNodesIndex()
                if isinstance(link_nodes, tuple):
                    start_nodes, end_nodes = link_nodes
                elif isinstance(link_nodes, np.ndarray):
                    if link_nodes.shape[1] == 2:
                        start_nodes, end_nodes = link_nodes[:, 0], link_nodes[:, 1]
                    else:
                        start_nodes, end_nodes = link_nodes[0, :], link_nodes[1, :]
                
                node1_id = node_names[int(start_nodes[i]) - 1]  # EPyT uses 1-based
                node2_id = node_names[int(end_nodes[i]) - 1]
                
                length = self.d.getLinkLength()[i]
                diameter = self.d.getLinkDiameter()[i]
                roughness = self.d.getLinkRoughnessCoeff()[i] if hasattr(self.d, 'getLinkRoughnessCoeff') else 100
                
                pipes.append({
                    'id': link_id,
                    'node1': node1_id,
                    'node2': node2_id,
                    'length': float(length),
                    'diameter': float(diameter),
                    'roughness': float(roughness)
                })
        
        # Extract tanks
        tanks = []
        for i, (node_id, node_type) in enumerate(zip(node_names, node_types)):
            if node_type == 'TANK':
                elevations = self.d.getNodeElevations()
                elevation = elevations[i] if hasattr(elevations, '__getitem__') else 0
                
                # Get tank properties
                init_level = self.d.getNodeTankInitialLevel()[i] if hasattr(self.d, 'getNodeTankInitialLevel') else 0
                min_level = self.d.getNodeTankMinimumWaterLevel()[i] if hasattr(self.d, 'getNodeTankMinimumWaterLevel') else 0
                max_level = self.d.getNodeTankMaximumWaterLevel()[i] if hasattr(self.d, 'getNodeTankMaximumWaterLevel') else 0
                diameter = self.d.getNodeTankDiameter()[i] if hasattr(self.d, 'getNodeTankDiameter') else 0
                
                coords = coords_dict.get(node_id, {})
                tanks.append({
                    'id': node_id,
                    'elevation': float(elevation),
                    'init_level': float(init_level),
                    'min_level': float(min_level),
                    'max_level': float(max_level),
                    'diameter': float(diameter),
                    'x': coords.get('x'),
                    'y': coords.get('y')
                })
        
        # Extract reservoirs
        reservoirs = []
        for i, (node_id, node_type) in enumerate(zip(node_names, node_types)):
            if node_type == 'RESERVOIR':
                heads = self.d.getNodeElevations()  # For reservoirs, elevation is head
                head = heads[i] if hasattr(heads, '__getitem__') else 0
                
                coords = coords_dict.get(node_id, {})
                reservoirs.append({
                    'id': node_id,
                    'head': float(head),
                    'x': coords.get('x'),
                    'y': coords.get('y')
                })
        
        return {
            'junctions': junctions,
            'pipes': pipes,
            'tanks': tanks,
            'reservoirs': reservoirs
        }
    
    def close(self):
        """Close the EPANET toolkit."""
        if self.d:
            self.d.unload()
            self.d = None



