#!/usr/bin/env python3
"""
Run Real-time EPANET Simulation Examples
========================================

This script provides an easy way to run all the real-time simulation examples.
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def run_example(script_name, description):
    """Run a Python script and handle errors"""
    print_header(f"Running: {description}")
    
    if not os.path.exists(script_name):
        print(f"❌ Script not found: {script_name}")
        return False
    
    try:
        print(f"Executing: python {script_name}")
        print("-" * 40)
        
        # Run the script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Script completed successfully")
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return True
        else:
            print("❌ Script failed")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Script timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def check_requirements():
    """Check if required packages are available"""
    print_header("Checking Requirements")
    
    required_packages = ['numpy', 'matplotlib', 'epyt']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_network_file():
    """Check if network file exists"""
    print_header("Checking Network File")
    
    network_file = "water-networks/Net1.inp"
    
    if os.path.exists(network_file):
        print(f"✅ Network file found: {network_file}")
        return True
    else:
        print(f"❌ Network file not found: {network_file}")
        print("Please ensure the network file exists")
        return False

def main():
    """Main function to run all examples"""
    print("Real-time EPANET Simulation Examples")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing packages.")
        return
    
    # Check network file
    if not check_network_file():
        print("\n❌ Network file check failed. Please ensure the network file exists.")
        return
    
    # List of examples to run
    examples = [
        ("test_realtime.py", "Test Suite - Verify all components work"),
        ("simple_realtime.py", "Simple Real-time Simulation - Basic example"),
        ("advanced_realtime.py", "Advanced Real-time Simulation - With control logic"),
        ("scada_integration.py", "SCADA Integration - Database logging and real-time data")
    ]
    
    print_header("Running Examples")
    
    results = {}
    
    for script, description in examples:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Script: {script}")
        print(f"{'='*60}")
        
        success = run_example(script, description)
        results[script] = success
        
        if success:
            print(f"✅ {script} completed successfully")
        else:
            print(f"❌ {script} failed")
        
        # Wait a moment between examples
        time.sleep(2)
    
    # Summary
    print_header("Summary")
    
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"Results: {successful}/{total} examples completed successfully")
    
    for script, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {script}: {status}")
    
    if successful == total:
        print("\n🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("1. Check the generated plots and data files")
        print("2. Examine the database file (realtime_simulation.db)")
        print("3. Modify the examples to suit your needs")
        print("4. Integrate with your own SCADA systems")
    else:
        print(f"\n⚠️  {total - successful} examples failed")
        print("Please check the error messages above and fix any issues")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
