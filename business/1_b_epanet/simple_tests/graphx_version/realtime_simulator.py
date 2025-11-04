"""
Real-Time Simulator Module
Manages continuous hydraulic simulation with step-by-step execution
"""
from typing import Dict, Tuple, Optional, Callable
import time


class RealTimeSimulator:
    """Manages continuous hydraulic and quality simulation"""
    
    def __init__(self, epanet_model):
        """
        Initialize real-time simulator
        
        Args:
            epanet_model: EPyT epanet model instance
        """
        self.d = epanet_model
        self.current_time = 0
        self.time_history = []
        self.pressure_history = []
        self.flow_history = []
        self.demand_history = []
        self.is_initialized = False
        
    def initialize(self):
        """Initialize hydraulic analysis"""
        print("Initializing hydraulic analysis...")
        self.d.openHydraulicAnalysis()
        self.d.initializeHydraulicAnalysis()
        self.is_initialized = True
        print("✓ Hydraulic analysis initialized")
        
    def step(self) -> Tuple[Dict, int]:
        """
        Advance simulation by one hydraulic time step
        
        Returns:
            Tuple of (current_state dict, next time step in seconds)
        """
        if not self.is_initialized:
            raise RuntimeError("Simulator not initialized. Call initialize() first.")
        
        # Run hydraulic analysis for current time step
        t = self.d.runHydraulicAnalysis()
        
        # Collect current state
        current_state = {
            'time': t,
            'time_str': self._format_time(t),
            'pressures': self.d.getNodePressure(),
            'flows': self.d.getLinkFlows(),
            'demands': self.d.getNodeActualDemand(),
            'velocities': self.d.getLinkVelocity(),
            'node_ids': self.d.getNodeNameID(),
            'link_ids': self.d.getLinkNameID()
        }
        
        # Add tank-specific data if tanks exist
        tank_indices = self.d.getNodeTankIndex()
        if len(tank_indices) > 0:
            current_state['tank_levels'] = self.d.getNodeHydraulicHead(tank_indices)
            current_state['tank_ids'] = [self.d.getNodeNameID(idx) for idx in tank_indices]
        
        # Store history
        self.time_history.append(t)
        self.pressure_history.append(current_state['pressures'])
        self.flow_history.append(current_state['flows'])
        self.demand_history.append(current_state['demands'])
        
        # Advance to next time step
        tstep = self.d.nextHydraulicAnalysisStep()
        
        return current_state, tstep
    
    def run_continuous(self, callback: Optional[Callable] = None, 
                      max_steps: Optional[int] = None,
                      realtime_delay: float = 0):
        """
        Run continuous simulation with optional callback for each step
        
        Args:
            callback: Function to call with state data at each step
            max_steps: Maximum number of steps to run (None for full simulation)
            realtime_delay: Delay in seconds between steps (for real-time simulation)
        """
        self.initialize()
        tstep = 1
        step_count = 0
        
        print(f"\nStarting continuous simulation...")
        print(f"Simulation duration: {self.d.getTimeSimulationDuration() / 3600:.1f} hours")
        print(f"Hydraulic time step: {self.d.getTimeHydraulicStep() / 60:.0f} minutes")
        
        while tstep > 0:
            state, tstep = self.step()
            step_count += 1
            
            if callback:
                callback(state)
            
            # Print progress
            if step_count % 10 == 0:
                print(f"  Step {step_count}: t = {state['time_str']}")
            
            # Check max steps limit
            if max_steps and step_count >= max_steps:
                print(f"\nReached maximum steps ({max_steps}). Stopping simulation.")
                break
            
            # Add delay for real-time simulation
            if realtime_delay > 0:
                time.sleep(realtime_delay)
        
        self.close()
        print(f"\n✓ Simulation completed: {step_count} time steps processed")
    
    def close(self):
        """Close hydraulic analysis and free memory"""
        if self.is_initialized:
            self.d.closeHydraulicAnalysis()
            self.is_initialized = False
            print("✓ Hydraulic analysis closed")
    
    def get_history_summary(self) -> Dict:
        """Get summary statistics from simulation history"""
        import statistics
        
        if not self.time_history:
            return {}
        
        # Calculate statistics for pressures
        avg_pressures = [statistics.mean(p) for p in zip(*self.pressure_history)]
        min_pressures = [min(p) for p in zip(*self.pressure_history)]
        max_pressures = [max(p) for p in zip(*self.pressure_history)]
        
        # Calculate statistics for flows
        avg_flows = [statistics.mean(abs(f)) for f in zip(*self.flow_history)]
        
        summary = {
            'total_steps': len(self.time_history),
            'duration_hours': self.time_history[-1] / 3600 if self.time_history else 0,
            'avg_pressures': avg_pressures,
            'min_pressures': min_pressures,
            'max_pressures': max_pressures,
            'avg_flows': avg_flows
        }
        
        return summary
    
    @staticmethod
    def _format_time(seconds: int) -> str:
        """Format time in seconds to HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def __del__(self):
        """Destructor to ensure proper cleanup"""
        if self.is_initialized:
            try:
                self.close()
            except:
                pass
