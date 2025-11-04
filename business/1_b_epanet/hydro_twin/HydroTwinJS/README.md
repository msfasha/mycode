# HydroTwinJS 🌊

**Real-time EPANET Web Dashboard for Water Distribution Network Monitoring**

HydroTwinJS is a comprehensive web-based dashboard that provides real-time monitoring, analysis, and visualization of water distribution networks using EPANET simulation engine. Built with modern web technologies, it offers an intuitive interface for water utilities, engineers, and researchers.

## ✨ Features

### 🔄 Real-time Simulation
- **Live EPANET Integration**: Direct integration with epanet-js for real-time hydraulic simulations
- **Dynamic Model Updates**: Automatic model parameter updates based on live sensor data
- **Continuous Monitoring**: Scheduled simulation runs with configurable intervals
- **Performance Optimization**: Millisecond-level simulation execution for responsive updates

### 📊 Advanced Visualization
- **Interactive Network Maps**: Leaflet-based network visualization with real-time data overlay
- **Pressure Distribution**: Color-coded pressure visualization across the network
- **Flow Analysis**: Real-time flow rate monitoring and analysis
- **Historical Charts**: Trend analysis with interactive charts and graphs

### 🚨 Smart Alerting System
- **Real-time Alerts**: Automated alert generation based on pressure thresholds and anomalies
- **Severity Classification**: Critical, warning, and info-level alert categorization
- **Historical Tracking**: Complete alert history and management
- **Customizable Thresholds**: Configurable alert parameters for different scenarios

### 📈 Analytics & Reporting
- **Performance Metrics**: System efficiency calculations and KPI tracking
- **Data Export**: CSV, JSON, and Excel export capabilities
- **Historical Analysis**: Long-term trend analysis and reporting
- **Custom Dashboards**: Configurable dashboard layouts and widgets

### 🔌 Integration Capabilities
- **Sensor Data Integration**: Support for SCADA, MQTT, and REST API data sources
- **Database Storage**: SQLite database for historical data storage
- **WebSocket Communication**: Real-time data streaming to connected clients
- **RESTful API**: Complete API for external system integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HydroTwinJS Architecture                 │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React)                                          │
│  ├── Dashboard Components                                  │
│  ├── Network Map (Leaflet)                                │
│  ├── Analytics Charts (Recharts)                          │
│  └── Real-time Updates (WebSocket)                        │
├─────────────────────────────────────────────────────────────┤
│  Backend (Node.js)                                         │
│  ├── Express.js Server                                     │
│  ├── WebSocket Service                                     │
│  ├── Simulation Engine (epanet-js)                        │
│  └── Data Service (SQLite)                                │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                │
│  ├── Sensor Data (SCADA/MQTT/REST)                        │
│  ├── Database (SQLite)                                    │
│  └── Model Files (.inp)                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **npm** or **yarn**
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/HydroTwinJS.git
   cd HydroTwinJS
   ```

2. **Install dependencies**
   ```bash
   # Install server dependencies
   npm install

   # Install client dependencies
   cd client
   npm install
   cd ..
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp env.example .env

   # Edit configuration
   nano .env
   ```

4. **Start the application**
   ```bash
   # Development mode (both server and client)
   npm run dev

   # Or start individually
   npm run server    # Backend only
   npm run client    # Frontend only
   ```

5. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:3001
   - **WebSocket**: ws://localhost:3002

## ⚙️ Configuration

### Environment Variables

```env
# Server Configuration
PORT=3001
NODE_ENV=development

# Database Configuration
DB_PATH=./data/simulation.db

# Sensor Data API Configuration
SENSOR_API_URL=http://localhost:3000/api/sensors
SENSOR_UPDATE_INTERVAL=30000

# WebSocket Configuration
WS_PORT=3002

# EPANET Model Files
MODEL_INP_PATH=./models/network.inp
MODEL_RPT_PATH=./models/report.rpt
MODEL_OUT_PATH=./models/output.bin

# Client Configuration
CLIENT_PORT=3000
```

### Model Configuration

1. **Place your EPANET model file** in the `models/` directory
2. **Update the model path** in your environment configuration
3. **Configure sensor mappings** in the data service

## 📖 API Documentation

### Simulation Endpoints

- `GET /api/simulation/status` - Get simulation status
- `POST /api/simulation/run` - Run manual simulation
- `GET /api/simulation/results` - Get simulation results
- `GET /api/simulation/summary` - Get network summary

### Sensor Endpoints

- `GET /api/sensors` - Get all sensor data
- `GET /api/sensors/:type` - Get sensor data by type
- `GET /api/sensors/:type/:id` - Get specific sensor value

### Data Endpoints

- `GET /api/data/historical` - Get historical data
- `GET /api/data/alerts` - Get active alerts
- `POST /api/data/alerts` - Create new alert
- `GET /api/data/stats` - Get network statistics

### WebSocket Events

- `simulation_results` - Real-time simulation results
- `alert` - New alert notifications
- `status_update` - System status updates

## 🎯 Usage Examples

### Basic Simulation

```javascript
// Run simulation with sensor data
const response = await fetch('/api/simulation/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sensorData: {
      demands: { 'J1': 100, 'J2': 150 },
      pressures: { 'J1': 45, 'J2': 42 },
      tankLevels: { 'T1': 8.5 }
    }
  })
});

const results = await response.json();
console.log('Simulation results:', results);
```

### WebSocket Connection

```javascript
// Connect to real-time updates
const ws = new WebSocket('ws://localhost:3002/ws');

ws.onopen = () => {
  console.log('Connected to HydroTwinJS');
  
  // Subscribe to simulation results
  ws.send(JSON.stringify({
    type: 'subscribe',
    subscriptions: ['simulation_results', 'alerts']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'simulation_results') {
    console.log('New simulation results:', data.data);
  } else if (data.type === 'alert') {
    console.log('New alert:', data.data);
  }
};
```

### Custom Sensor Integration

```javascript
// Custom sensor data processor
class CustomSensorService {
  async getSensorData() {
    // Fetch from your SCADA system
    const scadaData = await this.fetchFromSCADA();
    
    // Process and format data
    return {
      demands: this.processDemands(scadaData),
      pressures: this.processPressures(scadaData),
      flows: this.processFlows(scadaData)
    };
  }
  
  processDemands(data) {
    // Convert SCADA data to EPANET format
    return data.demandSensors.reduce((acc, sensor) => {
      acc[sensor.nodeId] = sensor.value;
      return acc;
    }, {});
  }
}
```

## 🔧 Development

### Project Structure

```
HydroTwinJS/
├── server/                 # Backend server
│   ├── index.js           # Main server file
│   ├── services/          # Core services
│   │   ├── SimulationEngine.js
│   │   ├── DataService.js
│   │   └── WebSocketService.js
│   └── routes/            # API routes
│       ├── simulation.js
│       ├── sensors.js
│       └── data.js
├── client/                # React frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── App.js         # Main app component
│   └── public/            # Static assets
├── models/                # EPANET model files
├── data/                  # Database files
└── docs/                  # Documentation
```

### Development Commands

```bash
# Install all dependencies
npm run install-all

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Lint code
npm run lint
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY server/ ./server/
COPY client/build ./client/build

EXPOSE 3001
CMD ["node", "server/index.js"]
```

### Production Build

```bash
# Build client
cd client
npm run build

# Start production server
cd ..
npm start
```

### Environment Setup

```bash
# Production environment
NODE_ENV=production
PORT=3001
DB_PATH=/data/simulation.db
MODEL_INP_PATH=/models/network.inp
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow the existing code style and patterns
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **EPANET**: The underlying hydraulic simulation engine
- **epanet-js**: JavaScript implementation of EPANET
- **React**: Frontend framework
- **Leaflet**: Interactive maps
- **Recharts**: Data visualization

## 📞 Support

- **Documentation**: [Wiki](https://github.com/your-org/HydroTwinJS/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/HydroTwinJS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/HydroTwinJS/discussions)
- **Email**: support@hydrotwinjs.com

## 🔮 Roadmap

- [ ] **Machine Learning Integration**: AI-powered anomaly detection
- [ ] **Mobile App**: Native mobile application
- [ ] **Cloud Deployment**: AWS/Azure deployment options
- [ ] **Advanced Analytics**: Predictive modeling capabilities
- [ ] **Multi-language Support**: Internationalization
- [ ] **Plugin System**: Extensible architecture for custom modules

---

**Built with ❤️ for the water industry**

*HydroTwinJS - Making water distribution networks smarter, one simulation at a time.*



