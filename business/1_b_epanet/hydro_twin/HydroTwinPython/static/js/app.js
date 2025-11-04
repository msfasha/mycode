// HydroTwin Web Application JavaScript

// Utility functions
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// API helper functions
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Simulation management
class SimulationManager {
    constructor() {
        this.isRunning = false;
        this.statusInterval = null;
    }
    
    async startSimulation(config) {
        try {
            const result = await apiCall('/api/run-simulation', {
                method: 'POST',
                body: JSON.stringify(config)
            });
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            this.isRunning = true;
            this.startStatusMonitoring();
            return result;
        } catch (error) {
            console.error('Failed to start simulation:', error);
            throw error;
        }
    }
    
    async stopSimulation() {
        try {
            await apiCall('/api/stop-simulation', {
                method: 'POST'
            });
            
            this.isRunning = false;
            this.stopStatusMonitoring();
        } catch (error) {
            console.error('Failed to stop simulation:', error);
            throw error;
        }
    }
    
    startStatusMonitoring() {
        this.statusInterval = setInterval(async () => {
            try {
                const status = await apiCall('/api/simulation-status');
                this.updateStatus(status);
                
                if (!status.running && this.isRunning) {
                    this.isRunning = false;
                    this.stopStatusMonitoring();
                    await this.loadResults();
                }
            } catch (error) {
                console.error('Status monitoring failed:', error);
            }
        }, 1000);
    }
    
    stopStatusMonitoring() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
        }
    }
    
    updateStatus(status) {
        // Update UI based on status
        const statusElement = document.getElementById('simulation-status');
        const progressBar = document.getElementById('progress-bar');
        const progressContainer = document.getElementById('progress-container');
        
        if (status.running) {
            if (statusElement) {
                statusElement.innerHTML = `<p><i class="fas fa-play-circle text-success"></i> Simulation running (${status.progress}%)</p>`;
            }
            if (progressBar) {
                progressBar.style.width = status.progress + '%';
            }
            if (progressContainer) {
                progressContainer.style.display = 'block';
            }
        } else if (status.error) {
            if (statusElement) {
                statusElement.innerHTML = `<p><i class="fas fa-exclamation-circle text-danger"></i> Error: ${status.error}</p>`;
            }
        } else {
            if (statusElement) {
                statusElement.innerHTML = `<p><i class="fas fa-check-circle text-success"></i> Simulation completed</p>`;
            }
        }
    }
    
    async loadResults() {
        try {
            const results = await apiCall('/api/simulation-results');
            this.displayResults(results);
            await this.generatePlots();
        } catch (error) {
            console.error('Failed to load results:', error);
        }
    }
    
    displayResults(results) {
        const container = document.getElementById('results-container');
        if (!container) return;
        
        let html = '<h6>Simulation Results:</h6>';
        
        if (results.network_info) {
            html += `<p><strong>Network:</strong> ${results.network_info.nodes} nodes, ${results.network_info.links} links</p>`;
        }
        
        if (results.simulation_results && results.simulation_results.length > 0) {
            const lastResult = results.simulation_results[results.simulation_results.length - 1];
            html += `<p><strong>Final Results:</strong></p>`;
            html += `<ul>`;
            html += `<li>Average Pressure: ${formatNumber(lastResult.avg_pressure)} m</li>`;
            html += `<li>Min Pressure: ${formatNumber(lastResult.min_pressure)} m</li>`;
            html += `<li>Max Pressure: ${formatNumber(lastResult.max_pressure)} m</li>`;
            html += `<li>Total Flow: ${formatNumber(lastResult.total_flow)} L/s</li>`;
            html += `</ul>`;
        }
        
        container.innerHTML = html;
    }
    
    async generatePlots() {
        const container = document.getElementById('plots-container');
        if (!container) return;
        
        try {
            // Generate pressure plot
            const pressureData = await apiCall('/api/generate-plot?type=pressure');
            if (pressureData.plot) {
                container.innerHTML = `
                    <h6>Pressure Over Time:</h6>
                    <img src="data:image/png;base64,${pressureData.plot}" class="img-fluid" alt="Pressure Plot">
                `;
            }
            
            // Generate flow plot
            const flowData = await apiCall('/api/generate-plot?type=flow');
            if (flowData.plot) {
                container.innerHTML += `
                    <h6 class="mt-3">Flow Over Time:</h6>
                    <img src="data:image/png;base64,${flowData.plot}" class="img-fluid" alt="Flow Plot">
                `;
            }
        } catch (error) {
            console.error('Failed to generate plots:', error);
        }
    }
}

// Monitoring management
class MonitoringManager {
    constructor() {
        this.isMonitoring = false;
        this.monitoringInterval = null;
    }
    
    startMonitoring() {
        this.isMonitoring = true;
        this.monitoringInterval = setInterval(async () => {
            if (!this.isMonitoring) return;
            
            try {
                const status = await apiCall('/api/simulation-status');
                this.updateMetrics(status);
                this.updateProgress(status);
                this.updateCharts(status);
                this.updateAlerts(status);
                this.updateControls(status);
            } catch (error) {
                console.error('Monitoring error:', error);
            }
        }, 2000); // Update every 2 seconds
    }
    
    stopMonitoring() {
        this.isMonitoring = false;
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
    }
    
    updateMetrics(status) {
        if (status.results && status.results.simulation_results) {
            const results = status.results.simulation_results;
            if (results.length > 0) {
                const latest = results[results.length - 1];
                
                const avgPressureEl = document.getElementById('avg-pressure');
                const totalFlowEl = document.getElementById('total-flow');
                const minPressureEl = document.getElementById('min-pressure');
                const maxPressureEl = document.getElementById('max-pressure');
                
                if (avgPressureEl) avgPressureEl.textContent = formatNumber(latest.avg_pressure);
                if (totalFlowEl) totalFlowEl.textContent = formatNumber(latest.total_flow);
                if (minPressureEl) minPressureEl.textContent = formatNumber(latest.min_pressure);
                if (maxPressureEl) maxPressureEl.textContent = formatNumber(latest.max_pressure);
            }
        }
    }
    
    updateProgress(status) {
        const statusDiv = document.getElementById('monitor-status');
        const progressBar = document.getElementById('monitor-progress-bar');
        const progressContainer = document.getElementById('monitor-progress-container');
        
        if (!statusDiv) return;
        
        if (status.running) {
            statusDiv.innerHTML = `<p><i class="fas fa-play-circle text-success"></i> Simulation running (${status.progress}%)</p>`;
            if (progressBar) {
                progressBar.style.width = status.progress + '%';
            }
            if (progressContainer) {
                progressContainer.style.display = 'block';
            }
        } else if (status.error) {
            statusDiv.innerHTML = `<p><i class="fas fa-exclamation-circle text-danger"></i> Error: ${status.error}</p>`;
        } else {
            statusDiv.innerHTML = '<p><i class="fas fa-check-circle text-success"></i> Simulation completed</p>';
        }
    }
    
    updateCharts(status) {
        const chartsDiv = document.getElementById('live-charts');
        if (!chartsDiv) return;
        
        if (status.results && status.results.simulation_results) {
            chartsDiv.innerHTML = '<p class="text-success"><i class="fas fa-chart-line"></i> Live data available</p>';
        }
    }
    
    updateAlerts(status) {
        const alertsDiv = document.getElementById('alerts-container');
        if (!alertsDiv) return;
        
        if (status.results && status.results.simulation_results) {
            const results = status.results.simulation_results;
            if (results.length > 0) {
                const latest = results[results.length - 1];
                let alerts = [];
                
                if (latest.min_pressure < 20) {
                    alerts.push('<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Low pressure detected!</div>');
                }
                
                if (latest.avg_pressure < 30) {
                    alerts.push('<div class="alert alert-info"><i class="fas fa-info-circle"></i> Average pressure below normal</div>');
                }
                
                if (alerts.length > 0) {
                    alertsDiv.innerHTML = alerts.join('');
                } else {
                    alertsDiv.innerHTML = '<p class="text-success"><i class="fas fa-check-circle"></i> All systems normal</p>';
                }
            }
        }
    }
    
    updateControls(status) {
        const controlsDiv = document.getElementById('controls-container');
        if (!controlsDiv) return;
        
        if (status.results && status.results.simulation_results) {
            const results = status.results.simulation_results;
            if (results.length > 0) {
                const latest = results[results.length - 1];
                let controls = [];
                
                if (latest.min_pressure < 20) {
                    controls.push('<div class="alert alert-primary"><i class="fas fa-cog"></i> Pressure boost recommended</div>');
                }
                
                if (latest.total_flow > 10000) {
                    controls.push('<div class="alert alert-info"><i class="fas fa-cog"></i> High flow detected - check system</div>');
                }
                
                if (controls.length > 0) {
                    controlsDiv.innerHTML = controls.join('');
                } else {
                    controlsDiv.innerHTML = '<p class="text-success"><i class="fas fa-check-circle"></i> No control actions needed</p>';
                }
            }
        }
    }
}

// Initialize managers
const simManager = new SimulationManager();
const monitoringManager = new MonitoringManager();

// Export for use in other scripts
window.SimulationManager = SimulationManager;
window.MonitoringManager = MonitoringManager;
window.simManager = simManager;
window.monitoringManager = monitoringManager;
window.formatNumber = formatNumber;
window.formatTime = formatTime;
