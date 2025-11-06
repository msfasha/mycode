
"""
Test monitoring engine with Extended Period Simulation.

This file is designed to verify that the MonitoringEngine class and associated
monitoring workflow for SCADA and EPANET Extended Period Simulations function as expected. 

Core functionalities tested include:
- Database connectivity and initialization
- Loading and parsing EPANET network files
- Establishing hydraulic baselines using BaselineEngine
- Running EPANET hydraulic simulation with real-world time-of-day patterns
- Simulating SCADA sensor data for pressures, flows, and tank levels
- Comparing simulated and expected data for monitoring and anomaly detection
- Storing and retrieving sensor readings and anomalies from the database

The tests in this script help ensure the monitoring backend is correctly configured
to:
    - Set up and run EPS using network files (.inp)
    - Generate, store, and retrieve synthetic and expected sensor data
    - Perform monitoring and anomaly detection routines needed by the application

Intended for manual and CI test use during backend development of the
water network monitoring and management system.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.monitoring_engine import MonitoringEngine
from services.scada_simulator import SCADASimulator
from services.baseline_engine import BaselineEngine
import database

async def test_monitoring():
    """Test complete monitoring workflow."""
    print("=" * 60)
    print("Testing Monitoring Engine with Extended Period Simulation")
    print("=" * 60)
    
    # Initialize database
    try:
        await database.init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return
    
    # Network file
    network_file = "../networks/yasmin.inp"
    if not Path(network_file).exists():
        print(f"✗ Network file not found: {network_file}")
        return
    
    print(f"\n1. Establishing baseline from {network_file}...")
    try:
        baseline_engine = BaselineEngine(network_file)
        baseline_data = baseline_engine.establish_baseline()
        print(f"✓ Baseline established")
        print(f"  - Junctions: {len(baseline_data['pressures'])}")
        print(f"  - Pipes: {len(baseline_data['flows'])}")
        print(f"  - Tanks: {len(baseline_data['tank_levels'])}")
        print(f"  - Demands: {len(baseline_data.get('demands', {}))}")
    except Exception as e:
        print(f"✗ Baseline establishment failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n2. Initializing monitoring engine with EPS...")
    try:
        monitor = MonitoringEngine(network_file, baseline_data)
        monitor.initialize_extended_period_simulation()
        print("✓ Monitoring engine initialized")
    except Exception as e:
        print(f"✗ Monitoring engine initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n3. Testing Extended Period Simulation step advancement...")
    try:
        current_time = datetime.now()
        expected = monitor.advance_one_step_and_get_expected(current_time)
        print(f"✓ EPS step advanced successfully")
        print(f"  - Expected pressures: {len(expected['pressures'])}")
        print(f"  - Expected flows: {len(expected['flows'])}")
        print(f"  - Expected tank levels: {len(expected['tank_levels'])}")
        print(f"  - Sample pressure: {list(expected['pressures'].values())[0] if expected['pressures'] else 'N/A'}")
    except Exception as e:
        print(f"✗ EPS step advancement failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n4. Testing SCADA data generation...")
    try:
        scada_sim = SCADASimulator(baseline_data)
        actual_readings = scada_sim.generate_sensor_data(
            current_time, current_time, interval_minutes=1
        )
        print(f"✓ SCADA data generated")
        print(f"  - Total readings: {len(actual_readings)}")
        print(f"  - Sample reading: {actual_readings[0] if actual_readings else 'N/A'}")
    except Exception as e:
        print(f"✗ SCADA generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n5. Testing anomaly detection...")
    try:
        # First comparison (should have some anomalies due to noise)
        anomalies = monitor.compare_and_detect_anomalies(
            expected, actual_readings
        )
        print(f"✓ Anomaly detection completed")
        print(f"  - Anomalies detected: {len(anomalies)}")
        if anomalies:
            print(f"  - Sample anomaly: {anomalies[0]}")
        else:
            print(f"  - No anomalies (within thresholds)")
    except Exception as e:
        print(f"✗ Anomaly detection failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n6. Testing database storage...")
    try:
        test_network_id = str(uuid.uuid4())
        
        # Store SCADA readings
        await database.store_scada_readings(test_network_id, actual_readings)
        print(f"✓ SCADA readings stored")
        
        # Store anomalies if any
        if anomalies:
            await database.store_anomalies(test_network_id, anomalies)
            print(f"✓ Anomalies stored: {len(anomalies)}")
            
            # Retrieve anomalies
            retrieved = await database.get_anomalies(test_network_id)
            print(f"✓ Anomalies retrieved: {len(retrieved)}")
        else:
            print(f"✓ No anomalies to store")
    except Exception as e:
        print(f"✗ Database storage failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n7. Testing multiple EPS steps...")
    try:
        # Advance a few more steps
        for step in range(3):
            expected = monitor.advance_one_step_and_get_expected(current_time)
            print(f"  Step {step + 1}: Simulation time = {monitor.current_simulation_time}s")
        print(f"✓ Multiple steps advanced successfully")
    except Exception as e:
        print(f"✗ Multiple steps failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n8. Cleanup...")
    try:
        monitor.cleanup()
        await database.close_db()
        print(f"✓ Cleanup completed")
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_monitoring())

