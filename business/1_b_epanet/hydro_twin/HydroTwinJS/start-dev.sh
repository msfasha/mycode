#!/bin/bash

# HydroTwinJS Development Startup Script
echo "🌊 Starting HydroTwinJS Development Environment..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v16 or higher."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please install Node.js v16 or higher."
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing server dependencies..."
    npm install
fi

if [ ! -d "client/node_modules" ]; then
    echo "📦 Installing client dependencies..."
    cd client && npm install && cd ..
fi

# Create necessary directories
mkdir -p data models logs

# Create sample model if it doesn't exist
if [ ! -f "models/network.inp" ]; then
    echo "📝 Creating sample EPANET model..."
    # The SimulationEngine will create a sample model automatically
fi

# Set environment variables
export NODE_ENV=development
export PORT=3001
export WS_PORT=3002
export DB_PATH=./data/simulation.db
export MODEL_INP_PATH=./models/network.inp
export MODEL_RPT_PATH=./models/report.rpt
export MODEL_OUT_PATH=./models/output.bin
export SENSOR_API_URL=http://localhost:3001/api/sensors
export SENSOR_UPDATE_INTERVAL=30000

echo "🚀 Starting development servers..."
echo "📊 Backend API: http://localhost:3001"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 WebSocket: ws://localhost:3002"
echo ""
echo "Press Ctrl+C to stop all servers"

# Start both servers concurrently
npm run dev


