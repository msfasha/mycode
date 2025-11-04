#!/bin/bash
# HydroTwin Environment Setup Script
# This script creates a Python virtual environment and installs all dependencies

set -e  # Exit on any error

echo "🌊 HydroTwin EPANET Real-time Simulation Environment Setup"
echo "========================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed from requirements.txt"
else
    echo "⚠️  requirements.txt not found. Installing core dependencies manually..."
    pip install epyt numpy matplotlib pandas scipy
fi

# Install additional EPANET dependencies if needed
echo "🔧 Installing EPANET toolkit dependencies..."
pip install epanet-toolkit 2>/dev/null || echo "⚠️  epanet-toolkit not available, using epyt only"

# Verify installation
echo "🧪 Verifying installation..."
python3 -c "
import sys
print(f'Python: {sys.version}')

try:
    import numpy as np
    print(f'✅ NumPy: {np.__version__}')
except ImportError as e:
    print(f'❌ NumPy import failed: {e}')

try:
    import matplotlib
    print(f'✅ Matplotlib: {matplotlib.__version__}')
except ImportError as e:
    print(f'❌ Matplotlib import failed: {e}')

try:
    from epyt import epanet
    print('✅ EPyT: Available')
except ImportError as e:
    print(f'❌ EPyT import failed: {e}')

try:
    import pandas as pd
    print(f'✅ Pandas: {pd.__version__}')
except ImportError as e:
    print(f'❌ Pandas import failed: {e}')
"

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the examples, use:"
echo "  python run_examples.py"
echo ""
echo "To deactivate the environment, run:"
echo "  deactivate"
