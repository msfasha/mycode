import time
import random
import pandas as pd
from datetime import datetime
from threading import Event, Thread
from epyt import epanet


# ================================================================
# 1. Simulate sensor data (replace with real API/MQTT later)
# ================================================================
def get_sensor_data(structure):
    """Return a dict of simulated real-time sensor data."""
    data = {
        "demands": {},
        "pump_status": {},
        "tank_levels": {},
    }

    for j in structure["junctions"]:
        data["demands"][j] = random.uniform(0.8, 1.2)

    for p in structure["pumps"]:
        data["pump_status"][p] = random.choice([0, 1])

    for t in structure["tanks"]:
        data["tank_levels"][t] = random.uniform(2.0, 6.0)

    return data


# ================================================================
# 2. One-cycle run (snapshot)
# ================================================================
def run_snapshot(inp_file, log_list):
    """Run one hydraulic snapshot using latest data."""
    d = epanet(inp_file)
    nodes = d.getNodeNameID()
    links = d.getLinkNameID()

    structure = {
        "junctions": [n for n, t in zip(nodes, d.getNodeType()) if t == 0],
        "tanks": [n for n, t in zip(nodes, d.getNodeType()) if t == 2],
        "pumps": [l for l, t in zip(links, d.getLinkType()) if t == 2],
    }

    # Get "live" data
    sensors = get_sensor_data(structure)

    # Apply updates
    for junc_id, factor in sensors["demands"].items():
        base = d.getNodeBaseDemands(junc_id)
        d.setNodeBaseDemands(junc_id, base * factor)

    for pump_id, status in sensors["pump_status"].items():
        d.setLinkStatus(pump_id, status)

    for tank_id, level in sensors["tank_levels"].items():
        try:
            d.setNodeTankLevel(tank_id, level)
        except Exception:
            pass  # skip if not supported

    # Solve hydraulics
    d.openHydraulicAnalysis()
    d.initializeHydraulicAnalysis()
    d.runHydraulicAnalysis()
    d.closeHydraulicAnalysis()

    pressure = d.getNodePressure()[0]
    flow = d.getLinkFlows()[0]
    timestamp = datetime.now()

    print(f"{timestamp:%H:%M:%S} | P={pressure:7.2f} m | Q={flow:7.2f} L/s")

    log_list.append({
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "pressure_m": pressure,
        "flow_Ls": flow,
    })

    # Clean up memory
    del d


# ================================================================
# 3. Repeating timer for real-time loop
# ================================================================
def run_digital_twin_realtime(inp_file, interval=10, cycles=10):
    """
    Run EPANET snapshot simulation repeatedly, every `interval` seconds.
    Each cycle reloads the network, reads sensor data, runs hydraulics,
    and logs results.
    """
    print("Starting timer-based EPANET digital twin...\n")
    stop_event = Event()
    logs = []

    def loop():
        for _ in range(cycles):
            if stop_event.is_set():
                break
            run_snapshot(inp_file, logs)
            time.sleep(interval)
        print("\nDigital twin loop completed.")

    thread = Thread(target=loop)
    thread.start()
    thread.join()

    # Convert logs to DataFrame
    df = pd.DataFrame(logs)
    df.to_csv("snapshot_results.csv", index=False)
    print("\nResults saved to snapshot_results.csv")
    return df


# ================================================================
# 4. Entry point
# ================================================================
if __name__ == "__main__":
    df = run_digital_twin_realtime("networks/Net1.inp", interval=5, cycles=20)
    print("\nFinal logged data:")
    print(df.head())
