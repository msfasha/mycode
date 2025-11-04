"""Service for establishing baseline from EPANET simulation."""
from pathlib import Path
from typing import Dict
from epyt import epanet
# NetworkLoader not needed in baseline_engine


class BaselineEngine:
    """Establishes baseline by running EPANET simulation."""
    
    def __init__(self, network_file: str):
        """Initialize with network file path."""
        self.network_file = network_file
        self.d = None
    
    def establish_baseline(self) -> Dict:
        """
        Run EPANET simulation with original network conditions.
        Returns baseline pressures, flows, and tank levels.
        """
        # Load network
        if not Path(self.network_file).exists():
            raise FileNotFoundError(f"Network file not found: {self.network_file}")
        
        self.d = epanet(self.network_file)
        
        try:
            # Run complete hydraulic simulation
            self.d.solveCompleteHydraulics()
            
            # Get node names and types
            node_names = self.d.getNodeNameID()
            node_types = self.d.getNodeType()
            
            # Get link names and types
            link_names = self.d.getLinkNameID()
            link_types = self.d.getLinkType()
            
            # Extract baseline pressures (at junctions and tanks)
            pressures = {}
            node_pressures = self.d.getNodePressure()
            
            for i, (node_id, node_type) in enumerate(zip(node_names, node_types)):
                if node_type in ['JUNCTION', 'TANK']:
                    pressures[node_id] = float(node_pressures[i]) if i < len(node_pressures) else 0.0
            
            # Extract baseline flows (in pipes)
            flows = {}
            link_flows = self.d.getLinkFlows()
            
            for i, (link_id, link_type) in enumerate(zip(link_names, link_types)):
                if link_type == 'PIPE':
                    flows[link_id] = float(link_flows[i]) if i < len(link_flows) else 0.0
            
            # Extract baseline tank levels
            tank_levels = {}
            try:
                node_tank_data = self.d.getNodeTankData()
                tank_indices = [i for i, nt in enumerate(node_types) if nt == 'TANK']
                
                for i, tank_idx in enumerate(tank_indices):
                    tank_id = node_names[tank_idx]
                    # Tank level is elevation + water level
                    elevation = self.d.getNodeElevations()[tank_idx]
                    try:
                        levels = self.d.getNodeTankInitialLevel()
                        initial_level = levels[tank_idx] if hasattr(levels, '__getitem__') else 0
                        tank_levels[tank_id] = float(elevation) + float(initial_level)
                    except:
                        tank_levels[tank_id] = float(elevation)
            except:
                # Fallback: use elevation as level
                for i, (node_id, node_type) in enumerate(zip(node_names, node_types)):
                    if node_type == 'TANK':
                        elevation = self.d.getNodeElevations()[i]
                        tank_levels[node_id] = float(elevation)
            
            # Extract baseline demands (for use in monitoring patterns)
            demands = {}
            for i, (node_id, node_type) in enumerate(zip(node_names, node_types)):
                if node_type == 'JUNCTION':
                    try:
                        demand_info = self.d.getNodeBaseDemands(i+1)
                        if demand_info and len(demand_info) > 1 and len(demand_info[1]) > 0:
                            demands[node_id] = float(demand_info[1][0])
                        else:
                            demands[node_id] = 0.0
                    except:
                        demands[node_id] = 0.0
            
            return {
                'pressures': pressures,
                'flows': flows,
                'tank_levels': tank_levels,
                'demands': demands
            }
        
        finally:
            # Close EPANET toolkit
            if self.d:
                self.d.unload()
                self.d = None

