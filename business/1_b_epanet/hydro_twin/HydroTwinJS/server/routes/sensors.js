const express = require('express');
const router = express.Router();

module.exports = (dataService) => {
  
  // Get latest sensor data
  router.get('/', async (req, res) => {
    try {
      const sensorData = await dataService.getLatestSensorData();
      
      res.json({
        success: true,
        data: sensorData,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        error: error.message 
      });
    }
  });

  // Get sensor data by type
  router.get('/:type', async (req, res) => {
    try {
      const { type } = req.params;
      const sensorData = await dataService.getLatestSensorData();
      
      let filteredData = {};
      
      switch (type) {
        case 'demands':
          filteredData = sensorData.demands || {};
          break;
        case 'pressures':
          filteredData = sensorData.pressures || {};
          break;
        case 'flows':
          filteredData = sensorData.flows || {};
          break;
        case 'tank-levels':
          filteredData = sensorData.tankLevels || {};
          break;
        case 'pump-status':
          filteredData = sensorData.pumpStatus || {};
          break;
        case 'valve-settings':
          filteredData = sensorData.valveSettings || {};
          break;
        default:
          return res.status(400).json({
            success: false,
            error: 'Invalid sensor type'
          });
      }
      
      res.json({
        success: true,
        type: type,
        data: filteredData,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      res.status(500).json({ 
        success: false,
        error: error.message 
      });
    }
  });

  // Get sensor data for specific node/link
  router.get('/:type/:id', async (req, res) => {
    try {
      const { type, id } = req.params;
      const sensorData = await dataService.getLatestSensorData();
      
      let value = null;
      
      switch (type) {
        case 'demand':
          value = sensorData.demands?.[id] || null;
          break;
        case 'pressure':
          value = sensorData.pressures?.[id] || null;
          break;
        case 'flow':
          value = sensorData.flows?.[id] || null;
          break;
        case 'tank-level':
          value = sensorData.tankLevels?.[id] || null;
          break;
        case 'pump-status':
          value = sensorData.pumpStatus?.[id] || null;
          break;
        case 'valve-setting':
          value = sensorData.valveSettings?.[id] || null;
          break;
        default:
          return res.status(400).json({
            success: false,
            error: 'Invalid sensor type'
          });
      }
      
      if (value === null) {
        return res.status(404).json({
          success: false,
          error: 'Sensor not found'
        });
      }
      
      res.json({
        success: true,
        sensor: {
          id: id,
          type: type,
          value: value,
          timestamp: new Date().toISOString()
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



