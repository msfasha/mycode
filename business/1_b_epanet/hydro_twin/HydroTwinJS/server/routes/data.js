const express = require('express');
const router = express.Router();

module.exports = (dataService) => {
  
  // Get historical data
  router.get('/historical', async (req, res) => {
    try {
      const limit = parseInt(req.query.limit) || 100;
      const data = await dataService.getHistoricalData(limit);
      
      res.json({
        success: true,
        data: data,
        count: data.length,
        limit: limit
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        error: error.message 
      });
    }
  });

  // Get alerts
  router.get('/alerts', async (req, res) => {
    try {
      const alerts = await dataService.getActiveAlerts();
      
      res.json({
        success: true,
        alerts: alerts,
        count: alerts.length
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        error: error.message 
      });
    }
  });

  // Create alert
  router.post('/alerts', async (req, res) => {
    try {
      const { 
        alertType, 
        severity, 
        message, 
        nodeId, 
        linkId, 
        value, 
        threshold 
      } = req.body;
      
      if (!alertType || !severity || !message) {
        return res.status(400).json({
          success: false,
          error: 'Missing required fields: alertType, severity, message'
        });
      }
      
      await dataService.createAlert(
        alertType, 
        severity, 
        message, 
        nodeId, 
        linkId, 
        value, 
        threshold
      );
      
      res.json({
        success: true,
        message: 'Alert created successfully'
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        error: error.message 
      });
    }
  });

  // Get network statistics
  router.get('/stats', async (req, res) => {
    try {
      const historicalData = await dataService.getHistoricalData(10);
      const alerts = await dataService.getActiveAlerts();
      
      const stats = {
        totalSimulations: historicalData.length,
        activeAlerts: alerts.length,
        averagePressure: 0,
        totalDemand: 0,
        systemStatus: 'operational'
      };
      
      if (historicalData.length > 0) {
        const latest = historicalData[0];
        stats.averagePressure = latest.average_pressure || 0;
        stats.totalDemand = latest.total_demand || 0;
      }
      
      if (alerts.length > 0) {
        const criticalAlerts = alerts.filter(alert => alert.severity === 'critical');
        stats.systemStatus = criticalAlerts.length > 0 ? 'critical' : 'warning';
      }
      
      res.json({
        success: true,
        stats: stats,
        timestamp: new Date().toISOString()
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



