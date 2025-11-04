"""Configuration settings for the backend."""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Network files storage
NETWORKS_DIR = BASE_DIR / "networks"
NETWORKS_DIR.mkdir(exist_ok=True)

# SCADA simulation settings
SCADA_UPDATE_INTERVAL_SECONDS = 60  # Generate data every minute
PRESSURE_NOISE_PERCENT = 2.0  # ±2% noise for pressure sensors
FLOW_NOISE_PERCENT = 3.0  # ±3% noise for flow sensors
LEVEL_NOISE_PERCENT = 1.0  # ±1% noise for tank level sensors

# Simulation duration (24 hours default)
SIMULATION_DURATION_HOURS = 24



