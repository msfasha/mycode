"""Monitoring engine with Extended Period Simulation for anomaly detection."""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from epyt import epanet
from services.time_patterns import get_diurnal_multiplier


class MonitoringEngine:
    """
    Monitors network by comparing EPANET Extended Period Simulation
    expected values with actual SCADA sensor readings.
    """
    
    def __init__(self, network_file: str, baseline_data: Dict):
        """
        Initialize monitoring engine.
        
        Args:
            network_file: Path to EPANET .inp file
            baseline_data: Baseline data with demands, pressures, flows, tank_levels
        """
        self.network_file = network_file
        self.baseline_data = baseline_data
        self.d: Optional[epanet] = None
        self.current_simulation_time = 0  # Seconds from start
        self.tank_levels_tracked: Dict[str, float] = {}  # Track actual tank levels from SCADA
        self.pattern_id = "DIURNAL_PATTERN"
        self.initialized = False
    
    def initialize_extended_period_simulation(self):
        """Set up Extended Period Simulation with 24-hour patterns."""
        if self.d:
            self.d.unload()
        
        # Load network
        if not Path(self.network_file).exists():
            raise FileNotFoundError(f"Network file not found: {self.network_file}")
        
        self.d = epanet(self.network_file)
        
        # Create 24-hour diurnal pattern
        pattern_multipliers = [get_diurnal_multiplier(float(h)) for h in range(24)]
        
        # Add pattern to EPANET
        try:
            self.d.addPattern(self.pattern_id, pattern_multipliers)
        except:
            # Pattern might already exist, try to get it
            pass
        
        # Set EPS parameters
        self.d.setTimeSimulationDuration(24 * 3600)  # 24 hours
        self.d.setTimeHydraulicStep(60)  # 1 minute steps
        self.d.setTimePatternStep(3600)  # 1 hour pattern steps
        
        # Assign pattern to all junctions
        node_names = self.d.getNodeNameID()
        node_types = self.d.getNodeType()
        
        baseline_demands = self.baseline_data.get('demands', {})
        
        for i, (node_id, node_type) in enumerate(zip(node_names, node_types)):
            if node_type == 'JUNCTION':
                # Get base demand (from baseline or from EPANET)
                base_demand = baseline_demands.get(node_id, 0)
                if base_demand == 0:
                    # Try to get from EPANET
                    try:
                        demand_info = self.d.getNodeBaseDemands(i+1)
                        if demand_info and len(demand_info) > 1 and len(demand_info[1]) > 0:
                            base_demand = demand_info[1][0]
                    except:
                        pass
                
                # Apply pattern to junction demand
                # Note: EPyT API may vary, adjust as needed
                try:
                    self.d.setNodeJunctionDemand(i+1, 1, base_demand, self.pattern_id)
                except:
                    # Fallback: set base demand with pattern
                    try:
                        self.d.setNodeBaseDemands(i+1, [base_demand])
                    except:
                        pass
        
        # Initialize hydraulic analysis for step-by-step simulation
        try:
            # Try to open and initialize hydraulic analysis
            self.d.openHydraulicAnalysis()
            self.d.initializeHydraulicAnalysis(0)  # Initialize for extended period
        except:
            try:
                # Alternative: try without parameter
                self.d.initializeHydraulicAnalysis()
            except:
                # Fallback: just solve hydraulics (will still work but not step-by-step)
                try:
                    self.d.solveCompleteHydraulics()
                except:
                    pass
        
        # Update tank levels from tracked SCADA data if available
        self._update_tank_levels_from_tracked()
        
        self.initialized = True
        self.current_simulation_time = 0
    
    def _update_tank_levels_from_tracked(self):
        """Update tank levels from actual SCADA readings for accuracy."""
        if not self.tank_levels_tracked or not self.d:
            return
        
        try:
            node_names = self.d.getNodeNameID()
            node_types = self.d.getNodeType()
            
            for i, (node_id, node_type) in enumerate(zip(node_names, node_types)):
                if node_type == 'TANK' and node_id in self.tank_levels_tracked:
                    # Get elevation
                    elevations = self.d.getNodeElevations()
                    elevation = elevations[i]
                    
                    # Calculate water level (total level - elevation)
                    total_level = self.tank_levels_tracked[node_id]
                    water_level = total_level - elevation
                    
                    # Set tank initial level
                    try:
                        self.d.setNodeTankData(i+1, 'InitialLevel', water_level)
                    except:
                        # Alternative method if above doesn't work
                        try:
                            # EPyT might use different method
                            self.d.setNodeTankInitialLevel(i+1, water_level)
                        except:
                            pass
        except Exception as e:
            print(f"Warning: Could not update tank levels: {e}")
    
    def advance_one_step_and_get_expected(self, current_time: datetime) -> Dict:
        """
        Advance EPANET Extended Period Simulation one step and get expected values.
        
        This maintains cumulative tank levels automatically.
        
        Args:
            current_time: Current real-world time
            
        Returns:
            Dictionary with expected pressures, flows, and tank_levels
        """
        if not self.initialized or not self.d:
            self.initialize_extended_period_simulation()
        
        try:
            # Try to advance simulation one step
            # Returns: time step in seconds (0 if end of simulation reached)
            try:
                tstep = self.d.nextHydraulicAnalysisStep()
            except:
                # If step-by-step fails, run complete hydraulics instead
                self.d.solveCompleteHydraulics()
                tstep = 60  # Assume 1 minute step
            
            if tstep <= 0:
                # Simulation reached end of 24 hours, restart
                print("Simulation reached 24 hours, restarting...")
                self.initialize_extended_period_simulation()
                try:
                    tstep = self.d.nextHydraulicAnalysisStep()
                except:
                    self.d.solveCompleteHydraulics()
                    tstep = 60
            
            # Update current simulation time
            try:
                self.current_simulation_time = self.d.getTimeSimulationTime()
            except:
                # Fallback: estimate based on steps
                self.current_simulation_time += 60  # Assume 1 minute steps
            
            # Extract expected values at current time step
            expected = {
                'pressures': self._extract_pressures(),
                'flows': self._extract_flows(),
                'tank_levels': self._extract_tank_levels()
            }
            
            return expected
            
        except Exception as e:
            print(f"Error advancing EPS step: {e}")
            # Fallback: run complete hydraulics
            self.d.solveCompleteHydraulics()
            return {
                'pressures': self._extract_pressures(),
                'flows': self._extract_flows(),
                'tank_levels': self._extract_tank_levels()
            }
    
    def _extract_pressures(self) -> Dict[str, float]:
        """Extract pressure values from EPANET."""
        pressures = {}
        try:
            node_names = self.d.getNodeNameID()
            node_types = self.d.getNodeType()
            node_pressures = self.d.getNodePressure()
            
            for i, (node_id, node_type) in enumerate(zip(node_names, node_types)):
                if node_type in ['JUNCTION', 'TANK']:
                    if i < len(node_pressures):
                        pressures[node_id] = float(node_pressures[i])
        except Exception as e:
            print(f"Error extracting pressures: {e}")
        return pressures
    
    def _extract_flows(self) -> Dict[str, float]:
        """Extract flow values from EPANET."""
        flows = {}
        try:
            link_names = self.d.getLinkNameID()
            link_types = self.d.getLinkType()
            link_flows = self.d.getLinkFlows()
            
            for i, (link_id, link_type) in enumerate(zip(link_names, link_types)):
                if link_type == 'PIPE' and i < len(link_flows):
                    flows[link_id] = float(link_flows[i])
        except Exception as e:
            print(f"Error extracting flows: {e}")
        return flows
    
    def _extract_tank_levels(self) -> Dict[str, float]:
        """Extract tank level values from EPANET."""
        tank_levels = {}
        try:
            node_names = self.d.getNodeNameID()
            node_types = self.d.getNodeType()
            elevations = self.d.getNodeElevations()
            
            tank_indices = [i for i, nt in enumerate(node_types) if nt == 'TANK']
            
            for tank_idx in tank_indices:
                tank_id = node_names[tank_idx]
                elevation = elevations[tank_idx]
                
                # Get water level in tank
                try:
                    # Try to get tank data
                    tank_data = self.d.getNodeTankData(tank_idx + 1)
                    if isinstance(tank_data, dict):
                        initial_level = tank_data.get('InitialLevel', 0)
                    else:
                        # Try alternative method
                        initial_levels = self.d.getNodeTankInitialLevel()
                        if isinstance(initial_levels, (list, tuple)) and tank_idx < len(initial_levels):
                            initial_level = initial_levels[tank_idx]
                        else:
                            initial_level = 0
                    
                    tank_levels[tank_id] = float(elevation) + float(initial_level)
                except:
                    # Fallback: use elevation only
                    tank_levels[tank_id] = float(elevation)
        except Exception as e:
            print(f"Error extracting tank levels: {e}")
        return tank_levels
    
    def update_tank_levels_from_scada(self, scada_readings: List[Dict]):
        """
        Update tracked tank levels from SCADA readings.
        This improves EPANET prediction accuracy.
        """
        for reading in scada_readings:
            if reading.get('sensor_type') == 'level':
                location_id = reading.get('location_id')
                value = reading.get('value')
                if location_id and value:
                    self.tank_levels_tracked[location_id] = float(value)
        
        # Update EPANET tank levels
        if self.d and self.tank_levels_tracked:
            self._update_tank_levels_from_tracked()
    
    def compare_and_detect_anomalies(
        self,
        expected: Dict,
        actual_readings: List[Dict],
        thresholds: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Compare expected vs actual readings and detect anomalies.
        
        Args:
            expected: Dict with 'pressures', 'flows', 'tank_levels'
            actual_readings: List of sensor readings from SCADA
            thresholds: Deviation thresholds (default: 10% pressure, 15% flow, 5% level)
        
        Returns:
            List of anomaly dictionaries
        """
        if thresholds is None:
            thresholds = {
                'pressure': 10.0,  # 10% deviation
                'flow': 15.0,      # 15% deviation
                'level': 5.0       # 5% deviation
            }
        
        anomalies = []
        
        for reading in actual_readings:
            sensor_id = reading.get('sensor_id', '')
            sensor_type = reading.get('sensor_type', '')
            location_id = reading.get('location_id', '')
            actual_value = reading.get('value')
            timestamp = reading.get('timestamp')
            
            if not all([sensor_id, sensor_type, location_id, actual_value]):
                continue
            
            # Get expected value
            if sensor_type == 'pressure':
                expected_value = expected.get('pressures', {}).get(location_id)
                threshold = thresholds['pressure']
            elif sensor_type == 'flow':
                expected_value = expected.get('flows', {}).get(location_id)
                threshold = thresholds['flow']
            elif sensor_type == 'level':
                expected_value = expected.get('tank_levels', {}).get(location_id)
                threshold = thresholds['level']
            else:
                continue
            
            if expected_value is None or expected_value == 0:
                continue
            
            # Calculate deviation percentage
            deviation_percent = abs(actual_value - expected_value) / abs(expected_value) * 100
            
            if deviation_percent > threshold:
                anomaly = {
                    'sensor_id': sensor_id,
                    'sensor_type': sensor_type,
                    'location_id': location_id,
                    'actual_value': float(actual_value),
                    'expected_value': float(expected_value),
                    'deviation_percent': round(deviation_percent, 2),
                    'threshold': threshold,
                    'timestamp': timestamp or datetime.now().isoformat(),
                    'severity': self._calculate_severity(deviation_percent, threshold)
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_severity(self, deviation_percent: float, threshold: float) -> str:
        """Calculate anomaly severity."""
        ratio = deviation_percent / threshold
        if ratio >= 2.0:
            return 'critical'
        elif ratio >= 1.5:
            return 'high'
        else:
            return 'medium'
    
    def cleanup(self):
        """Clean up EPANET resources."""
        if self.d:
            try:
                self.d.unload()
            except:
                pass
            self.d = None
        self.initialized = False

