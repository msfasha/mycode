import axios from 'axios';

class ApiService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`📤 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('❌ API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        console.log(`📥 API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('❌ API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Simulation endpoints
  async getSimulationStatus() {
    try {
      const response = await this.client.get('/simulation/status');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get simulation status: ${error.message}`);
    }
  }

  async runSimulation(sensorData = {}) {
    try {
      const response = await this.client.post('/simulation/run', { sensorData });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to run simulation: ${error.message}`);
    }
  }

  async getSimulationResults(limit = 10) {
    try {
      const response = await this.client.get(`/simulation/results?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get simulation results: ${error.message}`);
    }
  }

  async getSimulationSummary() {
    try {
      const response = await this.client.get('/simulation/summary');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get simulation summary: ${error.message}`);
    }
  }

  // Sensor endpoints
  async getSensorData() {
    try {
      const response = await this.client.get('/sensors');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get sensor data: ${error.message}`);
    }
  }

  async getSensorDataByType(type) {
    try {
      const response = await this.client.get(`/sensors/${type}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get sensor data by type: ${error.message}`);
    }
  }

  async getSensorValue(type, id) {
    try {
      const response = await this.client.get(`/sensors/${type}/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get sensor value: ${error.message}`);
    }
  }

  // Data endpoints
  async getHistoricalData(limit = 100) {
    try {
      const response = await this.client.get(`/data/historical?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get historical data: ${error.message}`);
    }
  }

  async getAlerts() {
    try {
      const response = await this.client.get('/data/alerts');
      return response.data.alerts || [];
    } catch (error) {
      throw new Error(`Failed to get alerts: ${error.message}`);
    }
  }

  async createAlert(alertData) {
    try {
      const response = await this.client.post('/data/alerts', alertData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create alert: ${error.message}`);
    }
  }

  async getNetworkStats() {
    try {
      const response = await this.client.get('/data/stats');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get network stats: ${error.message}`);
    }
  }

  // Utility methods
  async healthCheck() {
    try {
      const response = await this.client.get('/simulation/status');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  async ping() {
    try {
      const start = Date.now();
      await this.healthCheck();
      const end = Date.now();
      return end - start;
    } catch (error) {
      throw new Error(`Ping failed: ${error.message}`);
    }
  }
}

export { ApiService };



