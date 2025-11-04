"""Background simulation runner service with monitoring."""
import asyncio
from datetime import datetime
from typing import Dict, Optional
from services.scada_simulator import SCADASimulator
from services.monitoring_engine import MonitoringEngine
import database


class SimulationRunner:
    """Manages running simulations with monitoring and anomaly detection."""
    
    def __init__(self):
        self.running_simulations: Dict[str, asyncio.Task] = {}
        self.monitoring_engines: Dict[str, MonitoringEngine] = {}
    
    async def start_simulation(
        self, 
        network_id: str, 
        baseline_data: dict, 
        network_file: str,
        interval_minutes: int = 5
    ) -> bool:
        """
        Start continuous simulation with monitoring.
        
        Args:
            network_id: Unique network identifier
            baseline_data: Baseline pressures, flows, tank_levels, demands
            network_file: Path to EPANET .inp file
            interval_minutes: Monitoring interval (default: 5 minutes)
        """
        if network_id in self.running_simulations:
            return False  # Already running
        
        # Initialize SCADA simulator
        simulator = SCADASimulator(baseline_data)
        
        # Initialize monitoring engine with Extended Period Simulation
        monitor = MonitoringEngine(network_file, baseline_data)
        monitor.initialize_extended_period_simulation()
        self.monitoring_engines[network_id] = monitor
        
        interval_seconds = interval_minutes * 60
        
        async def monitoring_loop():
            """Monitoring loop: EPS step, SCADA generation, comparison, anomaly detection."""
            try:
                while network_id in self.running_simulations:
                    current_time = datetime.now()
                    
                    # Step 1: Advance EPANET EPS one step and get expected values
                    expected = monitor.advance_one_step_and_get_expected(current_time)
                    
                    # Step 2: Generate actual SCADA sensor readings
                    actual_readings = simulator.generate_sensor_data(
                        current_time, current_time, interval_minutes=1
                    )
                    
                    # Step 3: Update tank levels from actual SCADA for better accuracy
                    monitor.update_tank_levels_from_scada(actual_readings)
                    
                    # Step 4: Compare expected vs actual and detect anomalies
                    anomalies = monitor.compare_and_detect_anomalies(
                        expected, actual_readings
                    )
                    
                    # Step 5: Store SCADA readings in database
                    if actual_readings:
                        await database.store_scada_readings(network_id, actual_readings)
                    
                    # Step 6: Store anomalies if any detected
                    if anomalies:
                        await database.store_anomalies(network_id, anomalies)
                        print(f"[{network_id}] Detected {len(anomalies)} anomalies at {current_time}")
                    
                    # Wait for next monitoring interval
                    await asyncio.sleep(interval_seconds)
                    
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Error in monitoring loop for {network_id}: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # Cleanup
                if network_id in self.monitoring_engines:
                    monitor = self.monitoring_engines[network_id]
                    monitor.cleanup()
                    del self.monitoring_engines[network_id]
                
                if network_id in self.running_simulations:
                    del self.running_simulations[network_id]
        
        task = asyncio.create_task(monitoring_loop())
        self.running_simulations[network_id] = task
        return True
    
    async def stop_simulation(self, network_id: str) -> bool:
        """Stop simulation and cleanup monitoring engine."""
        if network_id in self.running_simulations:
            task = self.running_simulations[network_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Cleanup monitoring engine
            if network_id in self.monitoring_engines:
                self.monitoring_engines[network_id].cleanup()
                del self.monitoring_engines[network_id]
            
            del self.running_simulations[network_id]
            return True
        return False
    
    def is_running(self, network_id: str) -> bool:
        """Check if simulation is running for a network."""
        return network_id in self.running_simulations


# Global instance
simulation_runner = SimulationRunner()



