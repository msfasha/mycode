const express = require('express');
const router = express.Router();

module.exports = (simulationEngine, dataService) => {
  
  // Get simulation status
  router.get('/status', async (req, res) => {
    try {
      res.json({
        status: 'operational',
        engine_initialized: simulationEngine.isInitialized,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  // Run manual simulation
  router.post('/run', async (req, res) => {
    try {
      const sensorData = req.body.sensorData || {};
      const results = await simulationEngine.runSimulation(sensorData);
      
      // Store results
      await dataService.storeSimulationResults(results);
      
      res.json({
        success: true,
        results: results,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        error: error.message 
      });
    }
  });

  // Get simulation results
  router.get('/results', async (req, res) => {
    try {
      const limit = parseInt(req.query.limit) || 10;
      const results = await dataService.getHistoricalData(limit);
      
      res.json({
        success: true,
        data: results,
        count: results.length
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        error: error.message 
      });
    }
  });

  // Get network summary
  router.get('/summary', async (req, res) => {
    try {
      const latestResults = await dataService.getHistoricalData(1);
      
      if (latestResults.length === 0) {
        return res.json({
          success: true,
          summary: {
            totalNodes: 0,
            totalLinks: 0,
            totalDemand: 0,
            averagePressure: 0,
            status: 'no_data'
          }
        });
      }

      const latest = latestResults[0];
      res.json({
        success: true,
        summary: {
          totalNodes: Object.keys(latest.node_pressures || {}).length,
          totalLinks: Object.keys(latest.link_flows || {}).length,
          totalDemand: latest.total_demand,
          averagePressure: latest.average_pressure,
          status: 'operational',
          lastUpdate: latest.timestamp
        }
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        error: error.message 
      });
    }
  });

  return router;
};



