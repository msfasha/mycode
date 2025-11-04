#!/usr/bin/env python3
"""
Simple Real-time EPANET Simulation
==================================

A simplified example of real-time simulation using EPANET.
This example demonstrates:
1. Loading a network
2. Running step-by-step simulation
3. Reading sensor data
4. Implementing basic control logic

Usage: python simple_realtime.py
"""

import time
import numpy as np
from epyt import epanet

def simple_realtime_simulation():
    """Run a simple real-time simulation"""
    
    # Network file path
    network_file = "water-networks/Net1.inp"
    
    print("Simple Real-time EPANET Simulation")
    print("=" * 40)
    
    try:
        # Load network
        print("Loading network...")
        d = epanet(network_file)
        
        # Get network info
        print(f"Nodes: {d.getNodeCount()}")
        print(f"Links: {d.getLinkCount()}")
        print(f"Junctions: {d.getNodeJunctionCount()}")
        print(f"Tanks: {d.getNodeTankCount()}")
        
        # Get node and link IDs
        node_ids = d.getNodeNameID()
        link_ids = d.getLinkNameID()
        
        print(f"\nNode IDs: {node_ids}")
        print(f"Link IDs: {link_ids}")
        
        # Initialize hydraulic analysis
        print("\nInitializing hydraulic analysis...")
        d.openHydraulicAnalysis()
        d.initializeHydraulicAnalysis()
        
        # Simulation parameters
        time_step = 3600  # 1 hour
        total_time = 24 * 3600  # 24 hours
        current_time = 0
        
        print(f"\nStarting simulation...")
        print(f"Time step: {time_step} seconds (1 hour)")
        print(f"Total duration: {total_time/3600} hours")
        print("-" * 40)
        
        # Run simulation step by step
        while current_time < total_time:
            # Run hydraulic analysis
            d.runHydraulicAnalysis()
            
            # Get current results
            pressures = d.getNodePressure()
            flows = d.getLinkFlows()
            # Get tank levels - simplified approach
            tank_indices = d.getNodeTankIndex()
            tank_levels = []  # Simplified for now
            
            # Print status every hour
            if current_time % 3600 == 0:
                hour = current_time / 3600
                print(f"Time: {hour:2.0f}h - "
                      f"Avg Pressure: {np.mean(pressures):6.2f} m - "
                      f"Total Flow: {np.sum(np.abs(flows)):8.2f} L/s")
                
                # Show tank levels if any
                if len(tank_levels) > 0:
                    print(f"           Tank Levels: {tank_levels}")
            
            # Simple control logic example
            # If any pressure is too low, print warning
            min_pressure = np.min(pressures)
            if min_pressure < 20.0:
                print(f"  WARNING: Low pressure detected: {min_pressure:.2f} m")
            
            # Advance time
            current_time += time_step
            
            # Simulate real-time delay (remove in actual implementation)
            time.sleep(0.1)  # 100ms delay
        
        print("-" * 40)
        print("Simulation completed!")
        
        # Final results
        final_pressures = d.getNodePressure()
        final_flows = d.getLinkFlows()
        
        print(f"\nFinal Results:")
        print(f"Average Pressure: {np.mean(final_pressures):.2f} m")
        print(f"Min Pressure: {np.min(final_pressures):.2f} m")
        print(f"Max Pressure: {np.max(final_pressures):.2f} m")
        print(f"Total Flow: {np.sum(np.abs(final_flows)):.2f} L/s")
        
        # Close analysis
        d.closeHydraulicAnalysis()
        d.unload()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_realtime_simulation()
