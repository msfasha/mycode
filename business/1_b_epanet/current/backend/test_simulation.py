"""Simple test script to verify simulation works."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.simulation_runner import simulation_runner
from services.scada_simulator import SCADASimulator
from datetime import datetime
import database

async def test_simulation():
    """Test simulation runner."""
    print("Testing simulation system...")
    
    # Initialize database
    try:
        await database.init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return
    
    # Test baseline data
    test_baseline = {
        'pressures': {'29': 45.2, '31': 43.8},
        'flows': {'10': 2.5, '11': 1.8},
        'tank_levels': {'2': 970.5}
    }
    
    # Test SCADA simulator
    simulator = SCADASimulator(test_baseline)
    readings = simulator.generate_sensor_data(
        datetime.now(),
        datetime.now(),
        interval_minutes=1
    )
    print(f"✓ Generated {len(readings)} sensor readings")
    
    # Test storing in database
    import uuid
    test_network_id = str(uuid.uuid4())
    try:
        await database.store_scada_readings(test_network_id, readings)
        print("✓ Data stored in database")
        
        # Verify retrieval
        retrieved = await database.get_scada_readings(
            test_network_id,
            datetime.now(),
            datetime.now()
        )
        print(f"✓ Retrieved {len(retrieved)} readings from database")
    except Exception as e:
        print(f"✗ Database storage failed: {e}")
    
    # Test simulation runner
    try:
        success = await simulation_runner.start_simulation(test_network_id, test_baseline)
        if success:
            print("✓ Simulation started")
            await asyncio.sleep(2)
            await simulation_runner.stop_simulation(test_network_id)
            print("✓ Simulation stopped")
        else:
            print("✗ Failed to start simulation")
    except Exception as e:
        print(f"✗ Simulation runner failed: {e}")
    
    await database.close_db()
    print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(test_simulation())

