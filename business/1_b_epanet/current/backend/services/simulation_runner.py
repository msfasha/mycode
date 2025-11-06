"""Background simulation runner service with monitoring."""
import asyncio
from datetime import datetime
from typing import Dict, Optional, List
from services.scada_simulator import SCADASimulator
from services.monitoring_engine import MonitoringEngine
import database


class SimulationRunner:
    """Manages running simulations with monitoring and anomaly detection."""
    
    def __init__(self):
        self.running_simulations: Dict[str, asyncio.Task] = {}
        self.monitoring_engines: Dict[str, MonitoringEngine] = {}
        self.simulation_errors: Dict[str, List[Dict]] = {}  # Track errors per simulation
    
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
            consecutive_fatal_errors = 0
            max_fatal_errors = 3  # Stop after 3 consecutive fatal errors
            
            try:
                while network_id in self.running_simulations:
                    current_time = datetime.now()
                    
                    try:
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
                        
                        # Step 5: Store SCADA readings in database (non-fatal)
                        if actual_readings:
                            try:
                                await database.store_scada_readings(network_id, actual_readings)
                            except Exception as db_error:
                                error_msg = f"Failed to store SCADA readings: {db_error}"
                                print(f"[{network_id}] Warning: {error_msg}")
                                self._add_error(network_id, error_msg, "database", fatal=False)
                                # Continue simulation even if database write fails
                        
                        # Step 6: Store anomalies if any detected (non-fatal)
                        if anomalies:
                            print(f"[{network_id}] Detected {len(anomalies)} anomalies at {current_time}")
                            try:
                                await database.store_anomalies(network_id, anomalies)
                            except Exception as db_error:
                                error_msg = f"Failed to store anomalies: {db_error}"
                                print(f"[{network_id}] Warning: {error_msg}")
                                self._add_error(network_id, error_msg, "database", fatal=False)
                                # Continue simulation even if database write fails
                        
                        # Reset consecutive fatal errors on successful iteration
                        consecutive_fatal_errors = 0
                        
                    except (FileNotFoundError, ValueError, AttributeError) as fatal_error:
                        # Fatal errors: EPANET file issues, invalid data, etc.
                        error_msg = f"Fatal error in monitoring loop: {fatal_error}"
                        print(f"[{network_id}] {error_msg}")
                        import traceback
                        traceback.print_exc()
                        self._add_error(network_id, str(fatal_error), "fatal", fatal=True)
                        consecutive_fatal_errors += 1
                        
                        if consecutive_fatal_errors >= max_fatal_errors:
                            print(f"[{network_id}] Too many fatal errors, stopping simulation")
                            break
                        
                        # Wait before retrying
                        await asyncio.sleep(5)
                        continue
                        
                    except Exception as recoverable_error:
                        # Recoverable errors: EPANET API issues, temporary problems
                        error_msg = f"Recoverable error in monitoring loop: {recoverable_error}"
                        print(f"[{network_id}] Warning: {error_msg}")
                        self._add_error(network_id, str(recoverable_error), "recoverable", fatal=False)
                        # Continue simulation, try again next iteration
                    
                    # Wait for next monitoring interval
                    await asyncio.sleep(interval_seconds)
                    
            except asyncio.CancelledError:
                pass
            except Exception as e:
                error_msg = f"Critical error in monitoring loop: {e}"
                print(f"[{network_id}] {error_msg}")
                import traceback
                traceback.print_exc()
                self._add_error(network_id, str(e), "critical", fatal=True)
            finally:
                # Cleanup
                if network_id in self.monitoring_engines:
                    monitor = self.monitoring_engines[network_id]
                    monitor.cleanup()
                    del self.monitoring_engines[network_id]
                
                if network_id in self.running_simulations:
                    del self.running_simulations[network_id]
                
                # Keep errors for a while after simulation stops (for debugging)
                # Errors will be cleaned up when simulation is restarted
        
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
    
    def _add_error(self, network_id: str, error_message: str, error_type: str, fatal: bool = False):
        """Add error to error tracking for a simulation."""
        if network_id not in self.simulation_errors:
            self.simulation_errors[network_id] = []
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': error_message,
            'type': error_type,
            'fatal': fatal
        }
        
        self.simulation_errors[network_id].append(error_entry)
        
        # Keep only last 100 errors per simulation
        if len(self.simulation_errors[network_id]) > 100:
            self.simulation_errors[network_id] = self.simulation_errors[network_id][-100:]
    
    def get_errors(self, network_id: str) -> List[Dict]:
        """Get errors for a simulation."""
        return self.simulation_errors.get(network_id, [])
    
    def clear_errors(self, network_id: str):
        """Clear errors for a simulation."""
        if network_id in self.simulation_errors:
            del self.simulation_errors[network_id]


# Global instance
simulation_runner = SimulationRunner()



