"""
Main Monitoring System
Integrates SCADA simulator, real-time simulation, and dashboard
"""
import sys
import threading
import time
from pathlib import Path

try:
    from epyt import epanet
except ImportError:
    print("Error: EPyT library not found. Please install it with: pip install epyt")
    sys.exit(1)

from scada_simulator import SCADASimulator
from realtime_simulator import RealTimeSimulator
from network_dashboard import NetworkDashboard


class WaterNetworkMonitor:
    """Main monitoring system integrating all components"""
    
    def __init__(self, inp_file: str):
        """
        Initialize water network monitoring system
        
        Args:
            inp_file: Path to EPANET .inp file
        """
        print("\n" + "="*60)
        print("🌊 Water Network Monitoring System")
        print("="*60)
        
        # Validate input file
        if not Path(inp_file).exists():
            raise FileNotFoundError(f"EPANET input file not found: {inp_file}")
        
        print(f"Loading network: {inp_file}")
        
        # Load EPANET model
        self.d = epanet(inp_file)
        print(f"✓ Network loaded successfully")
        
        # Display network info
        self.print_network_info()
        
        # Initialize components
        print("\nInitializing system components...")
        self.simulator = RealTimeSimulator(self.d)
        self.scada = SCADASimulator(self.d)
        self.dashboard = NetworkDashboard(self.d)
        
        # Auto-deploy sensors
        self.scada.auto_deploy_sensors(num_pressure=10, num_flow=5)
        
        # Simulation control
        self.running = False
        self.simulation_thread = None
        
        print("✓ System initialization complete\n")
    
    def print_network_info(self):
        """Print network information"""
        print("\nNetwork Information:")
        print(f"  - Total Nodes: {self.d.getNodeCount()}")
        print(f"  - Junctions: {len(self.d.getNodeJunctionIndex())}")
        print(f"  - Reservoirs: {len(self.d.getNodeReservoirIndex())}")
        print(f"  - Tanks: {len(self.d.getNodeTankIndex())}")
        print(f"  - Total Links: {self.d.getLinkCount()}")
        print(f"  - Pipes: {len(self.d.getLinkPipeIndex())}")
        print(f"  - Pumps: {len(self.d.getLinkPumpIndex())}")
        print(f"  - Valves: {len(self.d.getLinkValveIndex())}")
        print(f"  - Simulation Duration: {self.d.getTimeSimulationDuration() / 3600:.1f} hours")
    
    def simulation_loop(self, max_steps: int = 50, update_interval: float = 1.0):
        """
        Main simulation loop running in separate thread
        
        Args:
            max_steps: Maximum number of simulation steps
            update_interval: Time between updates in seconds
        """
        try:
            self.simulator.initialize()
            tstep = 1
            step_count = 0
            
            print(f"\n{'='*60}")
            print("Starting simulation loop...")
            print(f"Max steps: {max_steps}")
            print(f"Update interval: {update_interval}s")
            print(f"{'='*60}\n")
            
            while tstep > 0 and self.running and step_count < max_steps:
                # Run simulation step
                state, tstep = self.simulator.step()
                step_count += 1
                
                # Get SCADA sensor readings
                sensor_data = self.scada.get_live_data(add_noise=True)
                
                # Merge sensor data with simulation state
                state.update({
                    'sensor_pressure': sensor_data.get('pressure', {}),
                    'sensor_flow': sensor_data.get('flow', {}),
                    'sensor_tank_level': sensor_data.get('tank_level', {})
                })
                
                # Update dashboard
                self.dashboard.update_state(state)
                
                # Print progress
                if step_count % 5 == 0:
                    print(f"  Step {step_count}/{max_steps}: t = {state['time_str']}")
                
                # Wait for next update
                time.sleep(update_interval)
            
            print(f"\n✓ Simulation loop completed: {step_count} steps")
            
            # Keep dashboard running even after simulation ends
            print("\nSimulation finished, but dashboard will continue displaying final state...")
            print("Press Ctrl+C to stop the dashboard")
            
        except Exception as e:
            print(f"\n❌ Error in simulation loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.simulator.close()
            self.running = False
    
    def start(self, max_steps: int = 50, update_interval: float = 1.0, 
             dashboard_port: int = 8050):
        """
        Start the monitoring system
        
        Args:
            max_steps: Maximum number of simulation steps
            update_interval: Time between updates in seconds
            dashboard_port: Port for dashboard server
        """
        self.running = True
        
        # Start simulation in separate thread
        self.simulation_thread = threading.Thread(
            target=self.simulation_loop,
            args=(max_steps, update_interval),
            daemon=True
        )
        self.simulation_thread.start()
        
        # Give simulation time to start
        time.sleep(2)
        
        # Start dashboard (blocks until stopped)
        try:
            self.dashboard.run(debug=False, port=dashboard_port)
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            self.stop()
    
    def stop(self):
        """Stop the monitoring system"""
        print("Stopping monitoring system...")
        self.running = False
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=5)
        print("✓ Monitoring system stopped")

def main():
    """Main entry point"""
    
    # Configuration
    INP_FILE = "networks/Net1.inp"  # Default network, change to yasmin.inp when available
    MAX_STEPS = 50  # Number of simulation steps (each step = hydraulic time step)
    UPDATE_INTERVAL = 1.0  # Seconds between updates
    DASHBOARD_PORT = 8050
    
    # Check if custom input file provided
    if len(sys.argv) > 1:
        INP_FILE = sys.argv[1]
    
    try:
        # Create and start monitoring system
        monitor = WaterNetworkMonitor(INP_FILE)
        monitor.start(
            max_steps=MAX_STEPS,
            update_interval=UPDATE_INTERVAL,
            dashboard_port=DASHBOARD_PORT
        )
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nUsage: python main_monitor.py [path/to/network.inp]")
        print("\nExample:")
        print("  python main_monitor.py Net1.inp")
        print("  python main_monitor.py yasmin.inp")
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
