"""
===============================================================================
EPANET Continuous Digital Twin Simulation (Simulation-Time Version)
===============================================================================

Author:        [Your Name]
Created:       [Date]
Compatible:    EPyT (EPANET Python Toolkit)
Python:        3.8+
File:          digital_twin_simtime.py

-------------------------------------------------------------------------------
DESCRIPTION
-------------------------------------------------------------------------------
This script implements a **continuous digital twin** simulation using the EPyT
(EPANET Python Toolkit). It continuously runs hydraulic analyses over time,
injecting synthetic SCADA-like data into the EPANET model at each iteration.

Unlike the real-time version, this implementation uses **EPANET’s internal
simulation time** (`t` and `tstep`) as the primary timeline rather than the
actual system clock. The simulation advances step-by-step according to the
network’s hydraulic time step and the user-defined loop interval.

At each iteration:
    1. Simulated SCADA data (demands, pumps, tanks) is generated.
    2. The EPANET model is updated using the Toolkit API.
    3. A hydraulic analysis step is executed.
    4. Node pressures and link flows are retrieved.
    5. Results are plotted live using matplotlib and stored in memory.
    6. The script sleeps for a user-defined interval before repeating.

This creates a continuously running **dynamic simulation** that mimics the
behavior of a real-time digital twin while remaining purely simulation-driven.

-------------------------------------------------------------------------------
FEATURES
-------------------------------------------------------------------------------
• Continuous simulation controlled by user-defined update interval  
• Dynamic injection of simulated SCADA data (demands, pumps, tanks)  
• Uses EPANET’s native hydraulic time tracking (seconds, hours)  
• Live matplotlib visualization of pressures and flows  
• Automatic CSV logging of results for analysis or postprocessing  
• Modular and extendable code structure (load, SCADA, visualize, run)

-------------------------------------------------------------------------------
STRUCTURE
-------------------------------------------------------------------------------
Functions:
    - load_network(inp_file)
          Loads the EPANET .inp file and extracts metadata such as
          node and link IDs, junctions, tanks, and pumps.
    - simulate_scada(structure)
          Generates random SCADA-like inputs for demands, pump statuses,
          and tank levels. Can be replaced with real sensor data sources.
    - update_live_plot(times, pressures, flows)
          Updates a live matplotlib plot with pressure and flow time series.
          X-axis represents EPANET simulation time.
    - run_digital_twin(inp_file, interval, max_steps)
          Main control loop that:
              • Fetches/updates SCADA data
              • Runs one hydraulic step
              • Records simulation results
              • Updates visualization
              • Waits for the next iteration

-------------------------------------------------------------------------------
USAGE
-------------------------------------------------------------------------------
$ python digital_twin_simtime.py

Configuration:
    inp_file  = Path to EPANET .inp network file (default: "networks/Net1.inp")
    interval  = Real-time pause between iterations, in seconds (default: 2)
    max_steps = Number of simulation steps to perform (default: 30)

Example:
    df = run_digital_twin("networks/Net1.inp", interval=2, max_steps=30)

Output:
    • Live chart displaying pressure (m) and flow (L/s)
    • Console log showing simulation time (s) and results
    • CSV file "twin_results.csv" containing time-series data

-------------------------------------------------------------------------------
NOTES
-------------------------------------------------------------------------------
• Requires EPyT (`pip install epyt`) and matplotlib (`pip install matplotlib`)
• The script uses `openHydraulicAnalysis()`, `runHydraulicAnalysis()`,
  and `nextHydraulicAnalysisStep()` to advance simulation time correctly.
• This version focuses on controlled, repeatable simulations rather than
  true real-time synchronization with the system clock.
• Ideal for testing, calibration, and algorithm development before deploying
  live sensor integration.

-------------------------------------------------------------------------------
REVISION HISTORY
-------------------------------------------------------------------------------
Version 1.0  - Initial continuous simulation version using EPANET simulation time.
Version 1.1  - Added SCADA data emulation and live plotting.

===============================================================================
"""

import time
import random
import pandas as pd
import matplotlib.pyplot as plt
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
        Simulate SCADA readings.
        - Junctions: demand multipliers (±20%)
        - Pumps: random ON/OFF states
        - Tanks: random level changes
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
# 3. Live Visualization
# =====================================
def update_live_plot(times, pressures, flows):
    plt.clf()
    plt.subplot(2, 1, 1)
    plt.plot(times, pressures, "-o", color="tab:blue")
    plt.title("EPANET Digital Twin — Live Monitoring")
    plt.ylabel("Pressure (m)")
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(times, flows, "-o", color="tab:orange")
    plt.ylabel("Flow (L/s)")
    plt.xlabel("Simulation Time (s)")
    plt.grid(True)

    plt.tight_layout()
    plt.pause(0.01)


# =====================================
# 4. Continuous Digital Twin Loop
# =====================================
def run_digital_twin(inp_file, interval=5, max_steps=25):
    """Run continuous EPANET simulation with live monitoring."""
    d, structure = load_network(inp_file)
    d.openHydraulicAnalysis()
    d.initializeHydraulicAnalysis()

    print("\nStarting continuous EPANET digital twin simulation...")
    print(f"Update interval: {interval} seconds\n")

    times, pressures, flows = [], [], []
    results = []

    plt.ion()
    plt.figure(figsize=(8, 6))

    try:
        step = 0
        while step < max_steps:
            scada = simulate_scada(structure)

            # --- Apply live SCADA data ---
            for junc_id, factor in scada["demands"].items():
                base = d.getNodeBaseDemands(junc_id)
                d.setNodeBaseDemands(junc_id, base * factor)

            for pump_id, status in scada["pump_status"].items():
                d.setLinkStatus(pump_id, status)

            for tank_id, level in scada["tank_levels"].items():
                d.setNodeTankLevel(tank_id, level)

            # --- Run hydraulics ---
            t = d.runHydraulicAnalysis()
            tstep = d.nextHydraulicAnalysisStep()

            pressure = d.getNodePressure()[0]
            flow = d.getLinkFlows()[0]

            times.append(t)
            pressures.append(pressure)
            flows.append(flow)
            results.append({"time": t, "pressure": pressure, "flow": flow})

            update_live_plot(times, pressures, flows)
            print(f"t = {t:6.1f} s | Pressure = {pressure:7.2f} m | Flow = {flow:7.2f} L/s")

            time.sleep(interval)
            step += 1

            if tstep <= 0:
                d.initializeHydraulicAnalysis()

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        # No d.close() or d.clean() in EPyT — the toolkit handles cleanup automatically
        plt.ioff()
        plt.show()
        print("EPANET simulation ended.")
        return pd.DataFrame(results)


# =====================================
# 5. Entry Point
# =====================================
if __name__ == "__main__":
    df = run_digital_twin("networks/Net1.inp", interval=2, max_steps=30)
    print("\nFinal logged data:")
    print(df.head())
    df.to_csv("twin_results.csv", index=False)
