const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const WebSocket = require('ws');
const http = require('http');
const path = require('path');
require('dotenv').config();

const SimulationEngine = require('./services/SimulationEngine');
const DataService = require('./services/DataService');
const WebSocketService = require('./services/WebSocketService');

const app = express();
const server = http.createServer(app);

// Middleware
app.use(helmet());
app.use(compression());
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../client/build')));

// Initialize services
const simulationEngine = new SimulationEngine();
const dataService = new DataService();
const wsService = new WebSocketService(server);

// API Routes
app.use('/api/simulation', require('./routes/simulation')(simulationEngine, dataService));
app.use('/api/sensors', require('./routes/sensors')(dataService));
app.use('/api/data', require('./routes/data')(dataService));

// Serve React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
});

// Initialize simulation engine
async function initialize() {
  try {
    // Try to initialize simulation engine, but don't fail if it doesn't work
    try {
      await simulationEngine.initialize();
      console.log('📊 Simulation engine ready');
    } catch (simError) {
      console.log('⚠️ Simulation engine not available, using mock data mode');
      console.log('   This is normal for development - the dashboard will still work with mock data');
    }
    
    await dataService.initialize();
    
    console.log('🚀 HydroTwinJS Server initialized successfully');
    console.log(`🔌 WebSocket server running on port ${process.env.WS_PORT || 3002}`);
    
    // Start real-time simulation loop
    startRealTimeSimulation();
    
  } catch (error) {
    console.error('❌ Failed to initialize server:', error);
    process.exit(1);
  }
}

// Real-time simulation loop
function startRealTimeSimulation() {
  const interval = parseInt(process.env.SENSOR_UPDATE_INTERVAL) || 5000; // 5 seconds for more responsive updates
  
  setInterval(async () => {
    try {
      console.log('🔄 Running real-time simulation...');
      
      // Fetch latest sensor data
      const sensorData = await dataService.getLatestSensorData();
      
      let results;
      if (simulationEngine.isInitialized) {
        // Use real EPANET simulation
        results = await simulationEngine.runSimulation(sensorData);
      } else {
        // Use mock simulation data
        results = generateMockSimulationResults(sensorData);
      }
      
      // Broadcast results to connected clients
      wsService.broadcastResults(results);
      
      // Store results in database
      await dataService.storeSimulationResults(results);
      
      console.log('✅ Simulation completed and results broadcasted');
      
    } catch (error) {
      console.error('❌ Simulation error:', error);
    }
  }, interval);
}

// Generate mock simulation results when EPANET engine is not available
function generateMockSimulationResults(sensorData) {
  const now = new Date();
  const hour = now.getHours();
  const minute = now.getMinutes();
  const timeOfDay = hour + minute / 60;
  
  // More realistic daily patterns
  const isPeakHour = (timeOfDay >= 6 && timeOfDay <= 9) || (timeOfDay >= 18 && timeOfDay <= 21);
  const isNightTime = timeOfDay >= 22 || timeOfDay <= 5;
  
  // Base values with realistic daily variation
  const baseDemand = isPeakHour ? 150 : isNightTime ? 30 : 100;
  const basePressure = isPeakHour ? 35 : isNightTime ? 50 : 40;
  
  // Add realistic network pressure drops
  const networkLoss = Math.random() * 20; // 0-20 PSI network loss
  
  // Generate realistic node data with proper pressure gradients
  const nodes = {};
  const nodeIds = ['J1', 'J2', 'J3', 'J4'];
  const baseElevations = [100, 95, 90, 85];
  
  nodeIds.forEach((nodeId, index) => {
    const elevation = baseElevations[index];
    const pressureDrop = (index * 5) + Math.random() * 3; // Progressive pressure drop
    const demand = sensorData.demands?.[nodeId] || (baseDemand * (0.2 + index * 0.1));
    const pressure = Math.max(10, basePressure - pressureDrop - networkLoss * (index / 3));
    const head = elevation + pressure * 2.31; // Convert PSI to feet
    
    nodes[nodeId] = {
      id: nodeId,
      type: 'EN_JUNCTION',
      head: Math.round(head * 10) / 10,
      pressure: Math.round(pressure * 10) / 10,
      demand: Math.round(demand * 10) / 10,
      quality: 0
    };
  });
  
  // Generate realistic pipe data
  const links = {};
  const pipeIds = ['P1', 'P2', 'P3', 'P4'];
  
  pipeIds.forEach((pipeId, index) => {
    const baseFlow = baseDemand * (0.8 - index * 0.1);
    const flowVariation = Math.random() * 20 - 10;
    const flow = Math.max(0, baseFlow + flowVariation);
    const velocity = Math.max(0.5, flow / 50 + Math.random() * 2); // Realistic velocity
    const headloss = Math.max(0, (index + 1) * 2 + Math.random() * 3);
    
    links[pipeId] = {
      id: pipeId,
      type: 'EN_PIPE',
      flow: Math.round(flow * 10) / 10,
      velocity: Math.round(velocity * 10) / 10,
      headloss: Math.round(headloss * 10) / 10,
      status: 1
    };
  });
  
  // Calculate realistic summary statistics
  const totalDemand = Object.values(nodes).reduce((sum, node) => sum + node.demand, 0);
  const totalFlow = Object.values(links).reduce((sum, link) => sum + Math.abs(link.flow), 0);
  const averagePressure = Object.values(nodes).reduce((sum, node) => sum + node.pressure, 0) / nodes.length;
  
  return {
    timestamp: now.toISOString(),
    nodes,
    links,
    summary: {
      totalDemand: Math.round(totalDemand * 10) / 10,
      totalFlow: Math.round(totalFlow * 10) / 10,
      averagePressure: Math.round(averagePressure * 10) / 10,
      simulationTime: 0
    }
  };
}

// Start server
const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`🌐 Server running on port ${PORT}`);
  initialize();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛑 Shutting down server...');
  simulationEngine.cleanup();
  server.close();
});

module.exports = app;

