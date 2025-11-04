"""
===============================================================================
EPANET Real-Time Digital Twin Simulation
===============================================================================

Author:        [Your Name]
Created:       [Date]
Compatible:    EPyT (EPANET Python Toolkit)
Python:        3.8+
File:          digital_twin_realtime.py

-------------------------------------------------------------------------------
DESCRIPTION
-------------------------------------------------------------------------------
This script implements a modular **digital twin** simulation for EPANET models
using the EPyT (EPANET Python Toolkit). It continuously runs hydraulic analyses
and synchronizes the simulation with the **real-world clock**, emulating live
SCADA operation.

At each update interval, the program:
    1. Reads or simulates real-time SCADA data (demands, pump status, tank levels)
    2. Updates the EPANET model dynamically through the Toolkit API
    3. Executes a hydraulic analysis step (`runHydraulicAnalysis`, `nextHydraulicAnalysisStep`)
    4. Retrieves and logs pressures, flows, and simulation time
    5. Visualizes results in real time with `matplotlib`
    6. Sleeps for the configured interval and repeats

The result is a continuously running model that reflects network state changes
over time — a foundation for a hydraulic **digital twin**.

-------------------------------------------------------------------------------
FEATURES
-------------------------------------------------------------------------------
• Real-time synchronization with the system clock (datetime.now)
• Dynamic injection of simulated or live SCADA data
• Live matplotlib visualization of pressures and flows
• CSV logging of results with timestamps and simulation times
• Modular design: independent functions for loading, SCADA simulation,
  visualization, and continuous loop control
• Compatible with any EPANET `.inp` network file

-------------------------------------------------------------------------------
STRUCTURE
-------------------------------------------------------------------------------
Functions:
    - load_network(inp_file)
          Loads the EPANET network and extracts node/link metadata.
    - simulate_scada(structure)
          Generates synthetic SCADA-like updates for junction demands, pumps,
          and tank levels (can be replaced with real sensor data sources).
    - update_live_plot(times, pressures, flows, sim_time)
          Updates a live dual-panel chart showing pressures and flows against
          real clock time, with current simulation time in the title.
    - run_digital_twin(inp_file, interval, max_steps)
          Main loop controlling the continuous simulation and data exchange
          between the SCADA layer and EPANET engine.

-------------------------------------------------------------------------------
USAGE
-------------------------------------------------------------------------------
$ python digital_twin_realtime.py

Configuration:
    inp_file  = Path to EPANET .inp network file (default: "networks/Net1.inp")
    interval  = Real-time delay between updates, in seconds (default: 3)
    max_steps = Number of update iterations before stopping (default: 25)

Example:
    df = run_digital_twin("networks/Net1.inp", interval=3, max_steps=25)

Output:
    - Live plot showing pressure (m) and flow (L/s)
    - Console printout of real time, simulation time, and results
    - CSV log: twin_results.csv

-------------------------------------------------------------------------------
NOTES
-------------------------------------------------------------------------------
• Requires EPyT package (`pip install epyt`)
• Matplotlib must be in interactive mode (`plt.ion()`).
• The script preserves EPANET’s internal hydraulic solver logic while using
  the system clock for visualization and logging.
• This framework can be extended to interface with real SCADA/IoT data via
  MQTT, REST APIs, or databases.

-------------------------------------------------------------------------------
REVISION HISTORY
-------------------------------------------------------------------------------
Version 1.0  - Initial version with real-time plotting and SCADA simulation.
Version 1.1  - Added wall-clock synchronization and improved logging.

===============================================================================
"""

import time
import random
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from epyt import epanet


# =====================================
# 1. Load EPANET model and structure
# =====================================
def load_network(inp_file):
    """Load EPANET network and extract metadata."""
    d = epanet(inp_file)
    nodes = d.getNodeNameID()
    links = d.getLinkNameID()

    junctions = [n for n, t in zip(nodes, d.getNodeType()) if t == 0]
    reservoirs = [n for n, t in zip(nodes, d.getNodeType()) if t == 1]
    tanks = [n for n, t in zip(nodes, d.getNodeType()) if t == 2]
    pumps = [l for l, t in zip(links, d.getLinkType()) if t == 2]
    valves = [l for l, t in zip(links, d.getLinkType()) if t in (3, 4, 5)]

    print(f"Loaded {len(nodes)} nodes ({len(junctions)} junctions, {len(tanks)} tanks)")
    print(f"  Links: {len(links)} (Pumps: {len(pumps)}, Valves: {len(valves)})")

    return d, {
        "nodes": nodes,
        "junctions": junctions,
        "tanks": tanks,
        "pumps": pumps,
        "valves": valves,
    }


# =====================================
# 2. SCADA Simulation Layer
# =====================================
def simulate_scada(structure):
    """
    Simulate synthetic SCADA data.
    - Junctions: demand multipliers (±20%)
    - Pumps: random ON/OFF
    - Tanks: random level updates
    """
    scada = {
        "demands": {},
        "pump_status": {},
        "tank_levels": {},
    }

    for j in structure["junctions"]:
        scada["demands"][j] = random.uniform(0.8, 1.2)

    for p in structure["pumps"]:
        scada["pump_status"][p] = random.choice([0, 1])

    for t in structure["tanks"]:
        scada["tank_levels"][t] = random.uniform(2.0, 6.0)

    return scada


# =====================================
# 3. Live Visualization (Real-Time Clock)
# =====================================
def update_live_plot(times, pressures, flows, sim_time):
    """Update live plot with real-time X-axis."""
    plt.clf()

    plt.subplot(2, 1, 1)
    plt.plot(times, pressures, "-o", color="tab:blue")
    plt.title(f"EPANET Digital Twin — Live Monitoring  |  Simulation time: {sim_time/3600:.1f} h")
    plt.ylabel("Pressure (m)")
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(times, flows, "-o", color="tab:orange")
    plt.ylabel("Flow (L/s)")
    plt.xlabel("Real Time")
    plt.grid(True)

    plt.gcf().autofmt_xdate()  # Rotate timestamp labels
    plt.tight_layout()
    plt.pause(0.05)


# =====================================
# 4. Continuous Digital Twin Loop
# =====================================
def run_digital_twin(inp_file, interval=5, max_steps=30):
    """Run continuous EPANET simulation synced with real wall-clock time."""
    d, structure = load_network(inp_file)
    d.openHydraulicAnalysis()
    d.initializeHydraulicAnalysis()

    print("\nStarting real-time EPANET digital twin simulation...")
    print(f"Update interval: {interval} seconds\n")

    times, pressures, flows = [], [], []
    results = []

    plt.ion()
    plt.figure(figsize=(8, 6))

    try:
        step = 0
        while step < max_steps:
            scada = simulate_scada(structure)

            # --- Apply SCADA data to model ---
            for junc_id, factor in scada["demands"].items():
                base = d.getNodeBaseDemands(junc_id)
                d.setNodeBaseDemands(junc_id, base * factor)

            for pump_id, status in scada["pump_status"].items():
                d.setLinkStatus(pump_id, status)

            for tank_id, level in scada["tank_levels"].items():
                try:
                    d.setNodeTankLevel(tank_id, level)
                except Exception:
                    pass  # Some EPyT versions don't implement this

            # --- Run one hydraulic step ---
            t = d.runHydraulicAnalysis()           # EPANET simulation time
            tstep = d.nextHydraulicAnalysisStep()  # Must advance time

            # --- Log and visualize with real clock ---
            now = datetime.now()
            pressure = d.getNodePressure()[0]
            flow = d.getLinkFlows()[0]

            times.append(now)
            pressures.append(pressure)
            flows.append(flow)

            results.append({
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "simulation_time_s": t,
                "pressure_m": pressure,
                "flow_Ls": flow,
            })

            update_live_plot(times, pressures, flows, t)
            print(f"{now:%H:%M:%S} | SimTime={t:7.1f} s | P={pressure:7.2f} m | Q={flow:7.2f} L/s")

            time.sleep(interval)
            step += 1   

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        plt.ioff()
        plt.show()
        print("EPANET simulation ended.")
        return pd.DataFrame(results)


# =====================================
# 5. Entry Point
# =====================================
if __name__ == "__main__":
    df = run_digital_twin("networks/Net1.inp", interval=3, max_steps=25)
    print("\nFinal logged data:")
    print(df.head())
    df.to_csv("twin_results.csv", index=False)
