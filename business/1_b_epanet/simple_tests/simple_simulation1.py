import time
import random
from epyt import epanet

# === CONFIGURATION ===
INP_FILE = "networks/Net1.inp"          # your EPANET input file
RESULTS_FILE = "results.csv"      # optional CSV storage
UPDATE_INTERVAL = 10              # seconds between updates (real time)

# === INITIALIZE EPANET ===
d = epanet(INP_FILE)
d.openHydraulicAnalysis()
d.initializeHydraulicAnalysis()

print("Starting continuous EPANET simulation loop...")

# Optional: prepare CSV header
with open(RESULTS_FILE, "w") as f:
    f.write("time,pressure_1,flow_1\n")

# === CONTINUOUS LOOP ===
try:
    while True:
        # --- 1. Simulate fetching real-time demand data ---
        # Replace this with real sensor data (API, MQTT, etc.)
        new_demand = random.uniform(0.5, 2.0)  # example multiplier
        node_id = 2                            # example node index
        d.setNodeBaseDemands(node_id, new_demand)
        print(f"Updated Node {node_id} demand to {new_demand:.2f} L/s")

        # --- 2. Run one hydraulic analysis step ---
        t = d.runHydraulicAnalysis()

        # --- 3. Retrieve results ---
        pressures = d.getNodePressure()
        flows = d.getLinkFlows()
        print(f"t = {t} s | Pressure[1] = {pressures[0]:.2f} m | Flow[1] = {flows[0]:.2f} L/s")

        # --- 4. Save or send results ---
        with open(RESULTS_FILE, "a") as f:
            f.write(f"{t},{pressures[0]},{flows[0]}\n")

        # --- 5. Advance simulation clock ---
        tstep = d.nextHydraulicAnalysisStep()
        if tstep <= 0:
            print("Reached end of simulation duration — restarting clock.")
            d.initializeHydraulicAnalysis()

        # --- 6. Wait before next update ---
        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:
    print("\nSimulation stopped by user.")

finally:
    d.closeHydraulicAnalysis()
    d.clean()
    print("EPANET simulation closed cleanly.")
