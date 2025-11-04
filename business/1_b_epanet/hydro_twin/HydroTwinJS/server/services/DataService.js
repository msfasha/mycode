const sqlite3 = require('sqlite3').verbose();
const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

class DataService {
  constructor() {
    this.db = null;
    this.sensorApiUrl = process.env.SENSOR_API_URL || 'http://localhost:3000/api/sensors';
    this.dbPath = process.env.DB_PATH || './data/simulation.db';
  }

  async initialize() {
    try {
      console.log('🗄️ Initializing data service...');
      
      // Create data directory if it doesn't exist
      const dataDir = path.dirname(this.dbPath);
      await fs.mkdir(dataDir, { recursive: true });
      
      // Initialize database
      await this.initializeDatabase();
      
      console.log('✅ Data service initialized successfully');
      
    } catch (error) {
      console.error('❌ Failed to initialize data service:', error);
      throw error;
    }
  }

  async initializeDatabase() {
    return new Promise((resolve, reject) => {
      this.db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) {
          reject(err);
          return;
        }
        
        // Create tables
        this.createTables()
          .then(() => resolve())
          .catch(reject);
      });
    });
  }

  async createTables() {
    const queries = [
      // Sensor data table
      `CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_id TEXT NOT NULL,
        sensor_type TEXT NOT NULL,
        value REAL NOT NULL,
        unit TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        location TEXT,
        metadata TEXT
      )`,
      
      // Simulation results table
      `CREATE TABLE IF NOT EXISTS simulation_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        simulation_id TEXT NOT NULL,
        node_id TEXT,
        node_type TEXT,
        head REAL,
        pressure REAL,
        demand REAL,
        quality REAL,
        tank_level REAL,
        link_id TEXT,
        link_type TEXT,
        flow REAL,
        velocity REAL,
        headloss REAL,
        status INTEGER,
        energy REAL
      )`,
      
      // Simulation summary table
      `CREATE TABLE IF NOT EXISTS simulation_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        simulation_id TEXT NOT NULL,
        total_demand REAL,
        total_flow REAL,
        average_pressure REAL,
        simulation_time REAL,
        status TEXT DEFAULT 'completed'
      )`,
      
      // Alerts table
      `CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        alert_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        message TEXT NOT NULL,
        node_id TEXT,
        link_id TEXT,
        value REAL,
        threshold REAL,
        status TEXT DEFAULT 'active'
      )`
    ];

    for (const query of queries) {
      await this.runQuery(query);
    }
  }

  async runQuery(query, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(query, params, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id: this.lastID, changes: this.changes });
        }
      });
    });
  }

  async getQuery(query, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(query, params, (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  async allQuery(query, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(query, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  async getLatestSensorData() {
    try {
      // Try to fetch from external API first
      try {
        const response = await axios.get(this.sensorApiUrl, { timeout: 5000 });
        return this.processSensorData(response.data);
      } catch (apiError) {
        console.log('📡 External sensor API not available, using mock data');
        return this.getMockSensorData();
      }
    } catch (error) {
      console.error('❌ Failed to get sensor data:', error);
      return this.getMockSensorData();
    }
  }

  processSensorData(rawData) {
    const processedData = {
      demands: {},
      tankLevels: {},
      pumpStatus: {},
      valveSettings: {},
      pressures: {},
      flows: {}
    };

    // Process different types of sensor data
    if (Array.isArray(rawData)) {
      rawData.forEach(sensor => {
        const { id, type, value, unit } = sensor;
        
        switch (type) {
          case 'demand':
            processedData.demands[id] = value;
            break;
          case 'tank_level':
            processedData.tankLevels[id] = value;
            break;
          case 'pump_status':
            processedData.pumpStatus[id] = value;
            break;
          case 'valve_setting':
            processedData.valveSettings[id] = value;
            break;
          case 'pressure':
            processedData.pressures[id] = value;
            break;
          case 'flow':
            processedData.flows[id] = value;
            break;
        }
      });
    }

    return processedData;
  }

  getMockSensorData() {
    // Generate realistic mock sensor data with more variation
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();
    
    // Simulate daily demand pattern with more realistic variation
    const timeOfDay = hour + minute / 60;
    const baseDemand = 100;
    
    // Peak hours: 6-9 AM and 6-9 PM
    const isPeakHour = (timeOfDay >= 6 && timeOfDay <= 9) || (timeOfDay >= 18 && timeOfDay <= 21);
    const peakMultiplier = isPeakHour ? 1.5 : 0.7;
    
    // Add some randomness for more realistic variation
    const randomVariation = 0.8 + Math.random() * 0.4; // 0.8 to 1.2
    const demandMultiplier = peakMultiplier * randomVariation;
    
    // Generate more realistic pressure drops across the network
    const basePressure = 45;
    const pressureDrop = Math.random() * 15; // 0-15 PSI variation
    
    return {
      demands: {
        'J1': Math.max(0, baseDemand * demandMultiplier * 0.2 + (Math.random() - 0.5) * 20),
        'J2': Math.max(0, baseDemand * demandMultiplier * 0.3 + (Math.random() - 0.5) * 25),
        'J3': Math.max(0, baseDemand * demandMultiplier * 0.4 + (Math.random() - 0.5) * 30),
        'J4': Math.max(0, baseDemand * demandMultiplier * 0.5 + (Math.random() - 0.5) * 35)
      },
      tankLevels: {
        'T1': Math.max(2, Math.min(10, 5 + Math.sin(timeOfDay * Math.PI / 12) * 2 + Math.random() * 2))
      },
      pumpStatus: {
        'PUMP1': Math.random() > 0.05 ? 1 : 0 // 95% chance pump is on
      },
      valveSettings: {
        'VALVE1': Math.max(50, Math.min(100, 80 + Math.sin(timeOfDay * Math.PI / 6) * 10 + Math.random() * 10))
      },
      pressures: {
        'J1': Math.max(20, basePressure + Math.random() * 10 - pressureDrop * 0.1),
        'J2': Math.max(15, basePressure - 5 + Math.random() * 8 - pressureDrop * 0.3),
        'J3': Math.max(10, basePressure - 10 + Math.random() * 6 - pressureDrop * 0.5),
        'J4': Math.max(5, basePressure - 15 + Math.random() * 4 - pressureDrop * 0.7)
      },
      flows: {
        'P1': Math.max(0, 50 + Math.random() * 30 + (isPeakHour ? 20 : -10)),
        'P2': Math.max(0, 40 + Math.random() * 25 + (isPeakHour ? 15 : -8)),
        'P3': Math.max(0, 30 + Math.random() * 20 + (isPeakHour ? 10 : -5)),
        'P4': Math.max(0, 20 + Math.random() * 15 + (isPeakHour ? 8 : -3)),
        'P5': Math.max(0, 15 + Math.random() * 10 + (isPeakHour ? 5 : -2))
      }
    };
  }

  async storeSimulationResults(results) {
    try {
      const simulationId = `sim_${Date.now()}`;
      
      // Store simulation summary
      await this.runQuery(
        `INSERT INTO simulation_summary (simulation_id, total_demand, total_flow, average_pressure, simulation_time)
         VALUES (?, ?, ?, ?, ?)`,
        [
          simulationId,
          results.summary.totalDemand,
          results.summary.totalFlow,
          results.summary.averagePressure,
          results.summary.simulationTime
        ]
      );

      // Store node results
      for (const [nodeId, nodeData] of Object.entries(results.nodes)) {
        await this.runQuery(
          `INSERT INTO simulation_results (simulation_id, node_id, node_type, head, pressure, demand, quality, tank_level)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
          [
            simulationId,
            nodeId,
            nodeData.type,
            nodeData.head,
            nodeData.pressure,
            nodeData.demand,
            nodeData.quality,
            nodeData.tankLevel
          ]
        );
      }

      // Store link results
      for (const [linkId, linkData] of Object.entries(results.links)) {
        await this.runQuery(
          `INSERT INTO simulation_results (simulation_id, link_id, link_type, flow, velocity, headloss, status, energy)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
          [
            simulationId,
            linkId,
            linkData.type,
            linkData.flow,
            linkData.velocity,
            linkData.headloss,
            linkData.status,
            linkData.energy
          ]
        );
      }

      console.log('💾 Simulation results stored successfully');
      
    } catch (error) {
      console.error('❌ Failed to store simulation results:', error);
    }
  }

  async getHistoricalData(limit = 100) {
    try {
      const query = `
        SELECT s.*, 
               GROUP_CONCAT(sr.node_id || ':' || sr.pressure) as node_pressures,
               GROUP_CONCAT(sr.link_id || ':' || sr.flow) as link_flows
        FROM simulation_summary s
        LEFT JOIN simulation_results sr ON s.simulation_id = sr.simulation_id
        GROUP BY s.simulation_id
        ORDER BY s.timestamp DESC
        LIMIT ?
      `;
      
      return await this.allQuery(query, [limit]);
      
    } catch (error) {
      console.error('❌ Failed to get historical data:', error);
      return [];
    }
  }

  async createAlert(alertType, severity, message, nodeId = null, linkId = null, value = null, threshold = null) {
    try {
      await this.runQuery(
        `INSERT INTO alerts (alert_type, severity, message, node_id, link_id, value, threshold)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [alertType, severity, message, nodeId, linkId, value, threshold]
      );
      
      console.log(`🚨 Alert created: ${message}`);
      
    } catch (error) {
      console.error('❌ Failed to create alert:', error);
    }
  }

  async getActiveAlerts() {
    try {
      return await this.allQuery(
        `SELECT * FROM alerts WHERE status = 'active' ORDER BY timestamp DESC`
      );
    } catch (error) {
      console.error('❌ Failed to get active alerts:', error);
      return [];
    }
  }

  async close() {
    if (this.db) {
      return new Promise((resolve) => {
        this.db.close((err) => {
          if (err) {
            console.error('❌ Error closing database:', err);
          } else {
            console.log('🗄️ Database connection closed');
          }
          resolve();
        });
      });
    }
  }
}

module.exports = DataService;
