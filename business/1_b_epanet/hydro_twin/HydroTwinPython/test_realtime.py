#!/usr/bin/env python3
"""
Test script for real-time EPANET simulation
============================================

This script tests the real-time simulation examples to ensure they work correctly.
"""

import os
import sys
import subprocess
import time

def test_imports():
    """Test if required packages can be imported"""
    print("Testing imports...")
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✓ matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ matplotlib import failed: {e}")
        return False
    
    try:
        from epyt import epanet
        print("✓ epyt imported successfully")
    except ImportError as e:
        print(f"✗ epyt import failed: {e}")
        return False
    
    return True

def test_network_file():
    """Test if network file exists"""
    print("\nTesting network file...")
    
    network_file = "water-networks/Net1.inp"
    
    if os.path.exists(network_file):
        print(f"✓ Network file found: {network_file}")
        return True
    else:
        print(f"✗ Network file not found: {network_file}")
        print("Please ensure the network file exists")
        return False

def test_epyt_basic():
    """Test basic EPyT functionality"""
    print("\nTesting basic EPyT functionality...")
    
    try:
        from epyt import epanet
        
        # Test loading a network
        network_file = "water-networks/Net1.inp"
        if os.path.exists(network_file):
            d = epanet(network_file)
            
            # Test basic functions
            node_count = d.getNodeCount()
            link_count = d.getLinkCount()
            
            print(f"✓ Network loaded: {node_count} nodes, {link_count} links")
            
            # Test hydraulic analysis
            d.openHydraulicAnalysis()
            d.initializeHydraulicAnalysis()
            d.runHydraulicAnalysis()
            
            # Test getting results
            pressures = d.getNodePressure()
            flows = d.getLinkFlows()
            
            print(f"✓ Hydraulic analysis successful")
            print(f"  - Pressures: {len(pressures)} values")
            print(f"  - Flows: {len(flows)} values")
            
            d.closeHydraulicAnalysis()
            d.unload()
            
            return True
        else:
            print("✗ Network file not found")
            return False
            
    except Exception as e:
        print(f"✗ EPyT test failed: {e}")
        return False

def test_simple_realtime():
    """Test the simple real-time simulation"""
    print("\nTesting simple real-time simulation...")
    
    try:
        # Import the simple real-time module
        sys.path.append('.')
        from simple_realtime import simple_realtime_simulation
        
        print("✓ Simple real-time module imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ Simple real-time test failed: {e}")
        return False

def test_advanced_realtime():
    """Test the advanced real-time simulation"""
    print("\nTesting advanced real-time simulation...")
    
    try:
        # Import the advanced real-time module
        sys.path.append('.')
        from advanced_realtime import AdvancedRealTimeSimulator
        
        print("✓ Advanced real-time module imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ Advanced real-time test failed: {e}")
        return False

def run_quick_simulation():
    """Run a quick simulation test"""
    print("\nRunning quick simulation test...")
    
    try:
        from epyt import epanet
        import numpy as np
        
        network_file = "water-networks/Net1.inp"
        d = epanet(network_file)
        
        # Run a short simulation
        d.openHydraulicAnalysis()
        d.initializeHydraulicAnalysis()
        
        # Run a few time steps
        for i in range(3):
            d.runHydraulicAnalysis()
            pressures = d.getNodePressure()
            flows = d.getLinkFlows()
            
            print(f"  Step {i+1}: Avg Pressure = {np.mean(pressures):.2f} m, "
                  f"Total Flow = {np.sum(np.abs(flows)):.2f} L/s")
        
        d.closeHydraulicAnalysis()
        d.unload()
        
        print("✓ Quick simulation test passed")
        return True
        
    except Exception as e:
        print(f"✗ Quick simulation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Real-time EPANET Simulation Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Network File Test", test_network_file),
        ("EPyT Basic Test", test_epyt_basic),
        ("Simple Real-time Test", test_simple_realtime),
        ("Advanced Real-time Test", test_advanced_realtime),
        ("Quick Simulation Test", run_quick_simulation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! You're ready to run real-time simulations.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
