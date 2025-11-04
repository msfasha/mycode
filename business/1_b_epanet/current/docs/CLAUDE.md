# Real-Time Dynamic Water Network Monitoring System (RTDWMS)
## Production-Ready Digital Twin for Jordanian Water Distribution Networks

---

## 🎯 System Objective

To develop a **production-ready digital twin** for a water distribution network in Jordan, capable of:

* **Monitoring network status** - Real-time monitoring of water network health
* **Detecting anomalies** - Identifying leaks, pressure drops, flow issues, and other problems
* **Providing forecasting** - Predicting future network behavior and demand patterns
* **Alerting operators** - Notifying when problems occur or are predicted
* **Simulating SCADA data** - Generating realistic sensor data for testing and development
* **Running hydraulic analysis** - Using EPANET for physics-based network modeling
* **Interactive dashboard** - Modern web interface for visualization and control

### **Core Value Proposition**
The system's main value is **anomaly detection and monitoring**, not just data generation. It compares what sensors measure vs what EPANET predicts to identify problems in the water network.

## 🎯 **Agreed System Logic (Critical for Implementation)**

### **The Correct Approach:**
1. **Upload network file** → Parse EPANET .inp file
2. **Establish baseline** → Run hydraulic analysis with **original network design conditions** (from .inp file)
3. **Get base pressure values** → Extract baseline pressures, flows, and tank levels
4. **Generate realistic SCADA data** → Simulate sensor readings based on baseline + time-of-day variations
5. **Monitor for major drifts** → Compare current SCADA readings vs baseline to detect anomalies

### **Key Implementation Requirements:**
- **True Baseline**: Use original network design conditions from .inp file, not estimated demands
- **Drift Detection**: Compare current readings against established baseline
- **Anomaly Thresholds**: Flag deviations >10% for pressure, >15% for flow
- **Real-time Monitoring**: Continuous comparison of measured vs baseline values
- **Alert System**: Notify operators when anomalies are detected

### **Critical Success Factors:**
- **Baseline Establishment**: Must use original network design, not estimated demands
- **Independent Monitoring**: SCADA data generation must be independent of monitoring logic
- **Accurate Comparison**: Monitoring engine must compare measured vs baseline, not predicted vs measured
- **Logical Flow**: Upload → Baseline → Generate Data → Monitor Drifts → Alert

---

