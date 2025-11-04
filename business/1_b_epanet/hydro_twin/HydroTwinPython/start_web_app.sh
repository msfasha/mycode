#!/bin/bash
# HydroTwin Web Application Startup Script

echo "🌊 HydroTwin Web Application"
echo "============================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup_environment.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip install flask
fi

# Check if required packages are available
echo "🧪 Checking dependencies..."
python -c "
import sys
try:
    import numpy
    import matplotlib
    from epyt import epanet
    import flask
    print('✅ All dependencies available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Please run setup_environment.sh first."
    exit 1
fi

# Start the web application
echo "🚀 Starting HydroTwin Web Application..."
echo "Access the application at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
