#!/usr/bin/env python3
"""
HydroTwin Web Application
========================

Flask web application for running EPANET real-time simulations
with interactive web interface.

Features:
- Run different simulation types
- Real-time monitoring dashboard
- Interactive plots and visualizations
- SCADA integration interface
- Results download and export

Usage: python app.py
"""

import os
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from epyt import epanet
from network_visualizer import (
    plot_network_topology, 
    plot_pressure_distribution, 
    plot_flow_patterns,
    plot_comprehensive_network,
    plot_network_statistics,
    save_network_plot
)

app = Flask(__name__)
app.secret_key = 'hydrotwin_secret_key_2024'

# Global variables for simulation state
simulation_state = {
    'running': False,
    'current_simulator': None,
    'simulation_type': None,
    'results': None,
    'progress': 0,
    'error': None
}

class WebSimulationManager:
    """Manages simulations for the web interface"""
    
    def __init__(self):
        self.simulators = {}
        self.results = {}
        self.plots = {}
    
    def run_simulation(self, sim_type, network_file, duration_hours=1):
        """Run a simulation in a separate thread"""
        global simulation_state
        
        try:
            simulation_state['running'] = True
            simulation_state['progress'] = 0
            simulation_state['error'] = None
            
            if sim_type == 'simple':
                result = self._run_simple_simulation(network_file, duration_hours)
                
            elif sim_type == 'advanced':
                from advanced_realtime import AdvancedRealTimeSimulator
                simulator = AdvancedRealTimeSimulator(network_file)
                simulator.load_network()
                simulator.run_simulation(duration_hours)
                result = simulator.generate_report()
                
            elif sim_type == 'scada':
                from scada_integration import SCADAIntegratedSimulator
                simulator = SCADAIntegratedSimulator(network_file)
                simulator.run_simulation(duration_hours * 60)  # Convert to minutes
                result = simulator.generate_report()
                
            elif sim_type == 'comprehensive':
                from realtime_simulation import RealTimeSimulator
                simulator = RealTimeSimulator(network_file, duration_hours)
                simulator.run_simulation()
                result = simulator.generate_report()
            
            simulation_state['results'] = result
            simulation_state['running'] = False
            simulation_state['progress'] = 100
            
        except Exception as e:
            simulation_state['running'] = False
            simulation_state['error'] = str(e)
            print(f"Simulation error: {e}")
    
    def _run_simple_simulation(self, network_file, duration_hours):
        """Run simple simulation and return results"""
        try:
            d = epanet(network_file)
            
            # Get network info
            network_info = {
                'nodes': d.getNodeCount(),
                'links': d.getLinkCount(),
                'junctions': d.getNodeJunctionCount(),
                'tanks': d.getNodeTankCount()
            }
            
            # Initialize hydraulic analysis
            d.openHydraulicAnalysis()
            d.initializeHydraulicAnalysis()
            
            # Run simulation
            time_step = 3600  # 1 hour
            total_time = duration_hours * 3600
            current_time = 0
            results = []
            
            while current_time < total_time:
                d.runHydraulicAnalysis()
                
                pressures = d.getNodePressure()
                flows = d.getLinkFlows()
                
                results.append({
                    'time': current_time / 3600,  # Convert to hours
                    'avg_pressure': np.mean(pressures),
                    'min_pressure': np.min(pressures),
                    'max_pressure': np.max(pressures),
                    'total_flow': np.sum(np.abs(flows))
                })
                
                current_time += time_step
                simulation_state['progress'] = min(100, (current_time / total_time) * 100)
            
            d.closeHydraulicAnalysis()
            d.unload()
            
            return {
                'network_info': network_info,
                'simulation_results': results,
                'duration_hours': duration_hours
            }
            
        except Exception as e:
            raise Exception(f"Simple simulation failed: {str(e)}")
    
    def generate_plot(self, results, plot_type='pressure'):
        """Generate plot and return as base64 string"""
        if not results or 'simulation_results' not in results:
            return None
        
        try:
            data = results['simulation_results']
            times = [r['time'] for r in data]
            
            plt.figure(figsize=(10, 6))
            
            if plot_type == 'pressure':
                avg_pressures = [r['avg_pressure'] for r in data]
                min_pressures = [r['min_pressure'] for r in data]
                max_pressures = [r['max_pressure'] for r in data]
                
                plt.plot(times, avg_pressures, 'b-', linewidth=2, label='Average Pressure')
                plt.plot(times, min_pressures, 'r--', linewidth=1, label='Min Pressure')
                plt.plot(times, max_pressures, 'g--', linewidth=1, label='Max Pressure')
                plt.ylabel('Pressure (m)')
                plt.title('System Pressure Over Time')
                
            elif plot_type == 'flow':
                flows = [r['total_flow'] for r in data]
                plt.plot(times, flows, 'g-', linewidth=2)
                plt.ylabel('Total Flow (L/s)')
                plt.title('System Flow Over Time')
            
            plt.xlabel('Time (hours)')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            
            # Convert plot to base64 string
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
            
        except Exception as e:
            print(f"Plot generation error: {e}")
            return None

# Initialize simulation manager
sim_manager = WebSimulationManager()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/simulations')
def simulations():
    """Simulations page"""
    return render_template('simulations.html')

@app.route('/monitor')
def monitor():
    """Real-time monitoring page"""
    return render_template('monitor.html')

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve images from the images directory"""
    return send_from_directory('images', filename)

@app.route('/api/network-files')
def get_network_files():
    """Get available network files"""
    network_dir = 'water-networks'
    if os.path.exists(network_dir):
        files = [f for f in os.listdir(network_dir) if f.endswith('.inp')]
        return jsonify({'files': files})
    return jsonify({'files': []})

@app.route('/api/run-simulation', methods=['POST'])
def run_simulation():
    """Start a simulation"""
    global simulation_state
    
    data = request.get_json()
    sim_type = data.get('type', 'simple')
    network_file = data.get('network_file', 'water-networks/Net1.inp')
    duration = data.get('duration', 1)
    
    if simulation_state['running']:
        return jsonify({'error': 'Simulation already running'}), 400
    
    # Start simulation in background thread
    thread = threading.Thread(
        target=sim_manager.run_simulation,
        args=(sim_type, network_file, duration)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Simulation started', 'type': sim_type})

@app.route('/api/simulation-status')
def simulation_status():
    """Get current simulation status"""
    return jsonify(simulation_state)

@app.route('/api/simulation-results')
def simulation_results():
    """Get simulation results"""
    if simulation_state['results']:
        return jsonify(simulation_state['results'])
    return jsonify({'error': 'No results available'}), 404

@app.route('/api/generate-plot')
def generate_plot():
    """Generate plot for results"""
    plot_type = request.args.get('type', 'pressure')
    
    if not simulation_state['results']:
        return jsonify({'error': 'No results available'}), 404
    
    plot_data = sim_manager.generate_plot(simulation_state['results'], plot_type)
    
    if plot_data:
        return jsonify({'plot': plot_data})
    else:
        return jsonify({'error': 'Failed to generate plot'}), 500

@app.route('/api/stop-simulation', methods=['POST'])
def stop_simulation():
    """Stop current simulation"""
    global simulation_state
    simulation_state['running'] = False
    return jsonify({'message': 'Simulation stopped'})

@app.route('/api/download-results')
def download_results():
    """Download simulation results as JSON"""
    if not simulation_state['results']:
        return jsonify({'error': 'No results available'}), 404
    
    # Create temporary file
    filename = f"simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(simulation_state['results'], f, indent=2, default=str)
    
    return send_file(filename, as_attachment=True, download_name=filename)

@app.route('/api/network-info/<network_file>')
def get_network_info(network_file):
    """Get information about a network file"""
    try:
        full_path = f"water-networks/{network_file}"
        if not os.path.exists(full_path):
            return jsonify({'error': 'Network file not found'}), 404
        
        d = epanet(full_path)
        
        info = {
            'filename': network_file,
            'nodes': d.getNodeCount(),
            'links': d.getLinkCount(),
            'junctions': d.getNodeJunctionCount(),
            'tanks': d.getNodeTankCount(),
            'reservoirs': d.getNodeReservoirCount(),
            'pipes': d.getLinkPipeCount(),
            'pumps': d.getLinkPumpCount(),
            'valves': d.getLinkValveCount(),
            'node_ids': d.getNodeNameID(),
            'link_ids': d.getLinkNameID()
        }
        
        d.unload()
        return jsonify(info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/network-visualization/<network_file>')
def get_network_visualization(network_file):
    """Get network visualization as base64 image"""
    try:
        full_path = f"water-networks/{network_file}"
        if not os.path.exists(full_path):
            return jsonify({'error': 'Network file not found'}), 404
        
        viz_type = request.args.get('type', 'comprehensive')
        
        # Load network
        d = epanet(full_path)
        
        # Generate visualization
        img_buffer = io.BytesIO()
        
        if viz_type == 'topology':
            plot_network_topology(d, save_path=img_buffer)
        elif viz_type == 'pressure':
            plot_pressure_distribution(d, save_path=img_buffer)
        elif viz_type == 'flow':
            plot_flow_patterns(d, save_path=img_buffer)
        elif viz_type == 'comprehensive':
            plot_comprehensive_network(d, save_path=img_buffer)
        elif viz_type == 'statistics':
            plot_network_statistics(d, save_path=img_buffer)
        else:
            d.unload()
            return jsonify({'error': 'Invalid visualization type'}), 400
        
        d.unload()
        
        # Convert to base64
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return jsonify({
            'image': img_base64,
            'type': viz_type,
            'filename': network_file
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/network-visualization-save/<network_file>')
def save_network_visualization(network_file):
    """Save network visualization to file and return download link"""
    try:
        full_path = f"water-networks/{network_file}"
        if not os.path.exists(full_path):
            return jsonify({'error': 'Network file not found'}), 404
        
        viz_type = request.args.get('type', 'comprehensive')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"network_{network_file}_{viz_type}_{timestamp}.png"
        
        # Load network
        d = epanet(full_path)
        
        # Create visualizations directory if it doesn't exist
        viz_dir = 'visualizations'
        os.makedirs(viz_dir, exist_ok=True)
        
        # Save visualization to the visualizations directory
        filepath = os.path.join(viz_dir, filename)
        save_network_plot(d, filepath, viz_type)
        
        d.unload()
        
        return jsonify({
            'message': 'Visualization saved successfully',
            'filename': filename,
            'download_url': f'/api/download-visualization/{filename}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-visualization/<filename>')
def download_visualization(filename):
    """Download saved visualization file"""
    try:
        # Look for the file in the visualizations directory
        viz_dir = 'visualizations'
        filepath = os.path.join(viz_dir, filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('images', exist_ok=True)
    
    print("🌊 HydroTwin Web Application")
    print("=" * 40)
    print("Starting Flask server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    # Try different ports if 5000 is occupied
    import socket
    port = 5000
    while port < 5010:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
            break
        except OSError:
            port += 1
    
    if port >= 5010:
        print("❌ No available ports found (5000-5009)")
        exit(1)
    
    if port != 5000:
        print(f"⚠️  Port 5000 was occupied, using port {port}")
        print(f"Access the application at: http://localhost:{port}")
    
    app.run(debug=True, host='0.0.0.0', port=port)
