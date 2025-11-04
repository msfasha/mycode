const { Workspace, Project } = require('epanet-js');
const fs = require('fs').promises;
const path = require('path');

class SimulationEngine {
  constructor() {
    this.workspace = null;
    this.project = null;
    this.isInitialized = false;
    // Use absolute paths to avoid working directory issues
    const projectRoot = path.join(__dirname, '../../');
    this.modelPath = process.env.MODEL_INP_PATH || path.join(projectRoot, 'models/simple.inp');
    this.reportPath = process.env.MODEL_RPT_PATH || path.join(projectRoot, 'models/report.rpt');
    this.outputPath = process.env.MODEL_OUT_PATH || path.join(projectRoot, 'models/output.bin');
  }

  async initialize() {
    try {
      console.log('🔧 Initializing EPANET simulation engine...');
      console.log('📁 Model path:', this.modelPath);
      console.log('📁 Report path:', this.reportPath);
      console.log('📁 Output path:', this.outputPath);
      
      // Create workspace
      this.workspace = new Workspace();
      
      // Create project
      this.project = new Project(this.workspace);
      
      // Check if model file exists, create sample if not
      await this.ensureModelExists();
      
      // Open the model
      await this.project.open(this.modelPath, this.reportPath, this.outputPath);
      
      this.isInitialized = true;
      console.log('✅ Simulation engine initialized successfully');
      
    } catch (error) {
      console.error('❌ Failed to initialize simulation engine:', error);
      throw error;
    }
  }

  async ensureModelExists() {
    try {
      await fs.access(this.modelPath);
    } catch (error) {
      console.log('📝 Creating sample EPANET model...');
      await this.createSampleModel();
    }
  }

  async createSampleModel() {
    // Create models directory if it doesn't exist
    const modelsDir = path.dirname(this.modelPath);
    await fs.mkdir(modelsDir, { recursive: true });

    // Create a simple sample network
    const sampleModel = `[TITLE]
Sample Water Distribution Network

[JUNCTIONS]
;ID               Elevation    Demand       Pattern
J1                100          0            P1
J2                95           100          P1
J3                90           150          P1
J4                85           200          P1

[RESERVOIRS]
;ID               Head         Pattern
R1                120          P1

[TANKS]
;ID               Elevation    InitLevel    MinLevel    MaxLevel    Diameter    MinVol      VolCurve
T1                80           5            2           10          20          0

[PIPES]
;ID               Node1        Node2        Length      Diameter    Roughness   MinorLoss   Status
P1                R1           J1           1000        12          100         0           Open
P2                J1           J2           800         10          100         0           Open
P3                J2           J3           600         8           100         0           Open
P4                J3           J4           400         6           100         0           Open
P5                J4           T1           200         4           100         0           Open

[PUMPS]
;ID               Node1        Node2        Properties
PUMP1             T1           J1           HEAD 50 0 100

[VALVES]
;ID               Node1        Node2        Diameter    Type        Setting      MinorLoss
VALVE1            J2           J3           8           PRV         80          0

[PATTERNS]
;ID               Multipliers
P1                1.2 1.1 1.0 0.9 0.8 0.9 1.0 1.1 1.2 1.3 1.2 1.1 1.0 0.9 0.8 0.9 1.0 1.1 1.2 1.3 1.2 1.1 1.0 0.9

[CURVES]
;ID               X-Value      Y-Value
CURVE1            0            0
CURVE1            100          50
CURVE1            200          80
CURVE1            300          100

[CONTROLS]
;Control Rule
LINK P2 CLOSED IF NODE J2 BELOW 85

[OPTIONS]
Units               GPM
Headloss            H-W
Hydraulics          Use
Quality             None
Viscosity           1.0
Diffusivity         1.0
Specific Gravity    1.0
Trials              40
Accuracy            0.01
Unbalanced          Continue 10
Pattern             1
Demand Multiplier   1.0
Emitter Exponent    0.5
Quality Tolerance   0.01
Head Error          0.001
Flow Change         0.001
Minimum Pressure    0
Required Pressure   0
Pressure Exponent   0.5
Headloss Formula    H-W
Headloss Pattern    1
Quality Pattern     1
Demand Pattern      1
Emitter Pattern     1
Leakage On          No
Leakage Formula     H-W
Leakage Exponent    1.0
Leakage Coefficient 0.0
Leakage Exponent    1.0
Check Frequency     2
Maximum Check       10
Dampening Limit     0
Dampening Constant  1
Dampening Repeats   3
Convergence Limit   0.01
Status Report       No
Summary Report      Yes
Energy Report       No
Page Size           0
Page Offset         0
Report Start        0
Report Step         3600
Report Duration     86400
Report Time Step    3600
Start Time          12:00 AM
Halt Flag           No
Duration            24:00
Hydraulic Step      3600
Quality Step        300
Pattern Step        3600
Pattern Start       0
Report Step         3600
Start Clocktime     12:00 AM
Statistic           None

[REPORT]
Status              Yes
Summary             Yes
Energy              No
Nodes               All
Links               All

[COORDINATES]
;Node              X-Coord         Y-Coord
J1                 100             100
J2                 200             100
J3                 300             100
J4                 400             100
R1                 0               100
T1                 500             100

[VERTICES]
;Link              X-Coord         Y-Coord
P1                 50              100
P2                 150             100
P3                 250             100
P4                 350             100
P5                 450             100

[LABELS]
;X-Coord           Y-Coord         Label & Anchor Node
50                 50              Sample Network
`;

    await fs.writeFile(this.modelPath, sampleModel);
    console.log('✅ Sample model created');
  }

  async runSimulation(sensorData = {}) {
    if (!this.isInitialized) {
      throw new Error('Simulation engine not initialized');
    }

    try {
      console.log('🧮 Running EPANET simulation...');
      
      // Update model with sensor data
      await this.updateModelWithSensorData(sensorData);
      
      // Run the simulation
      await this.project.run();
      
      // Extract results
      const results = await this.extractResults();
      
      console.log('✅ Simulation completed successfully');
      return results;
      
    } catch (error) {
      console.error('❌ Simulation failed:', error);
      throw error;
    }
  }

  async updateModelWithSensorData(sensorData) {
    try {
      // Update node demands based on sensor data
      if (sensorData.demands) {
        for (const [nodeId, demand] of Object.entries(sensorData.demands)) {
          await this.project.setNodeValue(nodeId, 'EN_DEMAND', demand);
        }
      }

      // Update tank levels
      if (sensorData.tankLevels) {
        for (const [tankId, level] of Object.entries(sensorData.tankLevels)) {
          await this.project.setNodeValue(tankId, 'EN_TANKLEVEL', level);
        }
      }

      // Update pump status
      if (sensorData.pumpStatus) {
        for (const [pumpId, status] of Object.entries(sensorData.pumpStatus)) {
          await this.project.setLinkValue(pumpId, 'EN_STATUS', status);
        }
      }

      // Update valve settings
      if (sensorData.valveSettings) {
        for (const [valveId, setting] of Object.entries(sensorData.valveSettings)) {
          await this.project.setLinkValue(valveId, 'EN_SETTING', setting);
        }
      }

    } catch (error) {
      console.error('❌ Failed to update model with sensor data:', error);
      throw error;
    }
  }

  async extractResults() {
    try {
      const results = {
        timestamp: new Date().toISOString(),
        nodes: {},
        links: {},
        summary: {}
      };

      // Get node results (pressures, heads, demands)
      const nodeCount = await this.project.getNodeCount();
      for (let i = 0; i < nodeCount; i++) {
        const nodeId = await this.project.getNodeId(i);
        const nodeType = await this.project.getNodeType(nodeId);
        
        results.nodes[nodeId] = {
          id: nodeId,
          type: nodeType,
          head: await this.project.getNodeValue(nodeId, 'EN_HEAD'),
          pressure: await this.project.getNodeValue(nodeId, 'EN_PRESSURE'),
          demand: await this.project.getNodeValue(nodeId, 'EN_DEMAND'),
          quality: await this.project.getNodeValue(nodeId, 'EN_QUALITY')
        };

        if (nodeType === 'EN_TANK') {
          results.nodes[nodeId].tankLevel = await this.project.getNodeValue(nodeId, 'EN_TANKLEVEL');
        }
      }

      // Get link results (flows, velocities, headloss)
      const linkCount = await this.project.getLinkCount();
      for (let i = 0; i < linkCount; i++) {
        const linkId = await this.project.getLinkId(i);
        const linkType = await this.project.getLinkType(linkId);
        
        results.links[linkId] = {
          id: linkId,
          type: linkType,
          flow: await this.project.getLinkValue(linkId, 'EN_FLOW'),
          velocity: await this.project.getLinkValue(linkId, 'EN_VELOCITY'),
          headloss: await this.project.getLinkValue(linkId, 'EN_HEADLOSS'),
          status: await this.project.getLinkValue(linkId, 'EN_STATUS')
        };

        if (linkType === 'EN_PUMP') {
          results.links[linkId].energy = await this.project.getLinkValue(linkId, 'EN_ENERGY');
        }
      }

      // Get simulation summary
      results.summary = {
        totalDemand: Object.values(results.nodes).reduce((sum, node) => sum + (node.demand || 0), 0),
        totalFlow: Object.values(results.links).reduce((sum, link) => sum + Math.abs(link.flow || 0), 0),
        averagePressure: this.calculateAveragePressure(results.nodes),
        simulationTime: await this.project.getCurrentTime()
      };

      return results;

    } catch (error) {
      console.error('❌ Failed to extract results:', error);
      throw error;
    }
  }

  calculateAveragePressure(nodes) {
    const pressures = Object.values(nodes)
      .filter(node => node.pressure !== undefined && node.pressure > 0)
      .map(node => node.pressure);
    
    return pressures.length > 0 
      ? pressures.reduce((sum, pressure) => sum + pressure, 0) / pressures.length 
      : 0;
  }

  async cleanup() {
    try {
      if (this.project) {
        await this.project.close();
      }
      if (this.workspace) {
        this.workspace = null;
      }
      console.log('🧹 Simulation engine cleaned up');
    } catch (error) {
      console.error('❌ Error during cleanup:', error);
    }
  }
}

module.exports = SimulationEngine;
