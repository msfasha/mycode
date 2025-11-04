"""
Network Dashboard Module
Creates real-time interactive dashboard using Plotly Dash
"""
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from datetime import datetime
from collections import deque
import numpy as np


class NetworkDashboard:
    """Real-time dashboard for water network monitoring"""
    
    def __init__(self, epanet_model, max_history: int = 100):
        """
        Initialize network dashboard
        
        Args:
            epanet_model: EPyT epanet model instance
            max_history: Maximum number of historical data points to keep
        """
        self.d = epanet_model
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True)
        self.max_history = max_history
        
        # Data storage
        self.current_state = None
        self.time_history = deque(maxlen=max_history)
        self.pressure_history = {i: deque(maxlen=max_history) 
                                for i in range(self.d.getNodeCount())}
        self.flow_history = {i: deque(maxlen=max_history) 
                            for i in range(self.d.getLinkCount())}
        
        # Get network structure
        # Normalize node coordinates into explicit x/y arrays to avoid KeyError on dict-like returns
        self.node_x, self.node_y = self._load_coordinates()
        self.link_connections = self.d.getNodesConnectingLinksIndex()
        self.node_ids = self.d.getNodeNameID()
        self.link_ids = self.d.getLinkNameID()
        
        # Get node types
        self.junction_indices = self.d.getNodeJunctionIndex()
        self.reservoir_indices = self.d.getNodeReservoirIndex()
        self.tank_indices = self.d.getNodeTankIndex()
        
        self.setup_layout()
        self.setup_callbacks()

    def _load_coordinates(self):
        """Load node coordinates from EPyT and normalize to 0-based numpy arrays (x, y).
        Handles EPyT variants: getNodeCoordinates('x'|'y') and getNodeCoordinates(1|2),
        and both dict-like and list/array return types.
        """
        n = int(self.d.getNodeCount())
        x_vals = None
        y_vals = None
        # Try new-style API using 'x'/'y'
        try:
            x_vals = self.d.getNodeCoordinates('x')
            y_vals = self.d.getNodeCoordinates('y')
        except Exception:
            x_vals = None
            y_vals = None
        # Fallback to numeric selector 1->x, 2->y
        if x_vals is None or y_vals is None:
            try:
                x_vals = self.d.getNodeCoordinates(1)
                y_vals = self.d.getNodeCoordinates(2)
            except Exception:
                x_vals = None
                y_vals = None
        # Last resort: no selector (may return composite); try to unpack
        if x_vals is None or y_vals is None:
            try:
                coords = self.d.getNodeCoordinates()
                # coords may be a tuple/list like [x_list, y_list]
                if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                    x_vals, y_vals = coords[0], coords[1]
            except Exception:
                pass
        # Normalize to lists in node index order (1..n) -> 0-based arrays
        def normalize(vals):
            if vals is None:
                return [0.0] * n
            # If EPyT returns its EpytValues or dict-like keyed by 1-based indices
            if isinstance(vals, dict):
                return [float(vals.get(i, 0.0)) for i in range(1, n + 1)]
            # If it's a sequence (list/tuple/numpy) with length n, assume already in order
            try:
                if len(vals) == n:
                    return [float(v) for v in vals]
            except Exception:
                pass
            # As a safe fallback, attempt attribute access .to_dict()
            try:
                as_dict = vals.to_dict()  # type: ignore[attr-defined]
                if isinstance(as_dict, dict):
                    return [float(as_dict.get(i, 0.0)) for i in range(1, n + 1)]
            except Exception:
                pass
            # If none of the above, fill zeros to keep UI responsive
            return [0.0] * n

        x_arr = normalize(x_vals)
        y_arr = normalize(y_vals)
        return np.array(x_arr), np.array(y_arr)
    
    def setup_layout(self):
        """Create dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1('🌊 Water Network Real-Time Monitoring System',
                       style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 10}),
                html.H3('Yasmin Network - Amman, Jordan',
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': 0}),
            ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'marginBottom': '20px'}),
            
            # Status row
            html.Div([
                html.Div([
                    html.H4('System Status', style={'textAlign': 'center'}),
                    html.Div(id='system-status', style={'textAlign': 'center', 'fontSize': '24px'})
                ], className='four columns', style={'backgroundColor': '#fff', 'padding': '10px', 'margin': '5px', 'borderRadius': '5px'}),
                
                html.Div([
                    html.H4('Current Time', style={'textAlign': 'center'}),
                    html.Div(id='current-time', style={'textAlign': 'center', 'fontSize': '24px'})
                ], className='four columns', style={'backgroundColor': '#fff', 'padding': '10px', 'margin': '5px', 'borderRadius': '5px'}),
                
                html.Div([
                    html.H4('Active Sensors', style={'textAlign': 'center'}),
                    html.Div(id='sensor-count', style={'textAlign': 'center', 'fontSize': '24px'})
                ], className='four columns', style={'backgroundColor': '#fff', 'padding': '10px', 'margin': '5px', 'borderRadius': '5px'}),
            ], className='row'),
            
            # Main content
            html.Div([
                # Network map
                html.Div([
                    dcc.Graph(id='network-map', style={'height': '600px'})
                ], className='eight columns'),
                
                # Alerts and statistics
                html.Div([
                    html.H4('🚨 System Alerts'),
                    html.Div(id='alerts', style={'height': '250px', 'overflowY': 'scroll'}),
                    html.Hr(),
                    html.H4('📊 Network Statistics'),
                    html.Div(id='statistics')
                ], className='four columns', style={'backgroundColor': '#fff', 'padding': '10px', 'borderRadius': '5px'}),
            ], className='row'),
            
            # Trend charts
            html.Div([
                html.Div([
                    dcc.Graph(id='pressure-trend', style={'height': '300px'})
                ], className='six columns'),
                
                html.Div([
                    dcc.Graph(id='flow-trend', style={'height': '300px'})
                ], className='six columns'),
            ], className='row', style={'marginTop': '20px'}),
            
            # Update interval
            dcc.Interval(
                id='interval-component',
                interval=2000,  # Update every 2 seconds
                n_intervals=0
            ),
            
            # Hidden div to store state
            html.Div(id='hidden-state', style={'display': 'none'})
        ], style={'backgroundColor': '#f5f5f5', 'padding': '10px'})
    
    def setup_callbacks(self):
        """Setup real-time update callbacks"""
        
        @self.app.callback(
            [Output('network-map', 'figure'),
             Output('pressure-trend', 'figure'),
             Output('flow-trend', 'figure'),
             Output('alerts', 'children'),
             Output('statistics', 'children'),
             Output('system-status', 'children'),
             Output('current-time', 'children'),
             Output('sensor-count', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_dashboard(n):
            if self.current_state is None:
                return [{}] * 3 + ['No data'] * 5
            
            # Create visualizations
            network_fig = self.create_network_figure()
            pressure_fig = self.create_pressure_trend()
            flow_fig = self.create_flow_trend()
            
            # Generate alerts and statistics
            alerts = self.check_alerts()
            statistics = self.generate_statistics()
            
            # Status indicators
            status = html.Span('🟢 OPERATIONAL', style={'color': 'green', 'fontWeight': 'bold'})
            current_time = self.current_state.get('time_str', '--:--:--')
            sensor_count = f"{self.d.getNodeCount() + self.d.getLinkCount()} sensors"
            
            return network_fig, pressure_fig, flow_fig, alerts, statistics, status, current_time, sensor_count
    
    def create_network_figure(self):
        """Create network visualization with current state"""
        if self.current_state is None:
            return {}
        
        pressures = self.current_state.get('pressures', [])
        flows = self.current_state.get('flows', [])
        
        # Defensive: ensure coordinates are available
        if getattr(self, 'node_x', None) is None or getattr(self, 'node_y', None) is None:
            return {}

        # Create link traces (pipes)
        link_traces = []
        for i in range(len(self.link_connections[0])):
            from_node_idx = self.link_connections[0][i] - 1
            to_node_idx = self.link_connections[1][i] - 1
            
            # Color based on flow magnitude
            flow_val = abs(flows[i]) if i < len(flows) else 0
            color = f'rgb({min(255, int(flow_val * 5))}, {max(0, 100 - int(flow_val * 2))}, 150)'
            width = min(5, 1 + abs(flow_val) / 50)
            
            link_traces.append(go.Scatter(
                x=[self.node_x[from_node_idx], self.node_x[to_node_idx]],
                y=[self.node_y[from_node_idx], self.node_y[to_node_idx]],
                mode='lines',
                line=dict(color=color, width=width),
                hoverinfo='text',
                text=f'{self.link_ids[i]}<br>Flow: {flow_val:.2f} LPS',
                showlegend=False
            ))
        
        # Create node traces with different markers for different types
        node_traces = []
        
        # Junctions
        if len(self.junction_indices) > 0:
            junc_x = [self.node_x[i-1] for i in self.junction_indices]
            junc_y = [self.node_y[i-1] for i in self.junction_indices]
            junc_p = [pressures[i-1] for i in self.junction_indices]
            junc_text = [f'{self.node_ids[i-1]}<br>P: {pressures[i-1]:.2f} m' 
                        for i in self.junction_indices]
            
            node_traces.append(go.Scatter(
                x=junc_x, y=junc_y,
                mode='markers',
                marker=dict(
                    size=12,
                    color=junc_p,
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="Pressure (m)", x=1.15),
                    line=dict(width=1, color='white')
                ),
                text=junc_text,
                hoverinfo='text',
                name='Junctions'
            ))
        
        # Reservoirs
        if len(self.reservoir_indices) > 0:
            res_x = [self.node_x[i-1] for i in self.reservoir_indices]
            res_y = [self.node_y[i-1] for i in self.reservoir_indices]
            res_text = [f'{self.node_ids[i-1]}<br>Reservoir' for i in self.reservoir_indices]
            
            node_traces.append(go.Scatter(
                x=res_x, y=res_y,
                mode='markers',
                marker=dict(size=20, color='blue', symbol='square', 
                           line=dict(width=2, color='white')),
                text=res_text,
                hoverinfo='text',
                name='Reservoirs'
            ))
        
        # Tanks
        if len(self.tank_indices) > 0:
            tank_x = [self.node_x[i-1] for i in self.tank_indices]
            tank_y = [self.node_y[i-1] for i in self.tank_indices]
            tank_text = [f'{self.node_ids[i-1]}<br>Tank' for i in self.tank_indices]
            
            node_traces.append(go.Scatter(
                x=tank_x, y=tank_y,
                mode='markers',
                marker=dict(size=20, color='orange', symbol='diamond',
                           line=dict(width=2, color='white')),
                text=tank_text,
                hoverinfo='text',
                name='Tanks'
            ))
        
        layout = go.Layout(
            title='Network Status Map',
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=True, zeroline=False, title='X Coordinate'),
            yaxis=dict(showgrid=True, zeroline=False, title='Y Coordinate'),
            plot_bgcolor='#f9f9f9',
            legend=dict(x=0, y=1)
        )
        
        return {'data': link_traces + node_traces, 'layout': layout}
    
    def create_pressure_trend(self):
        """Create pressure trend chart"""
        if len(self.time_history) == 0:
            return {}
        
        # Plot trends for first few junctions
        traces = []
        for i in range(min(5, len(self.junction_indices))):
            idx = self.junction_indices[i] - 1
            traces.append(go.Scatter(
                x=list(self.time_history),
                y=list(self.pressure_history[idx]),
                mode='lines',
                name=self.node_ids[idx]
            ))
        
        layout = go.Layout(
            title='Pressure Trends',
            xaxis=dict(title='Simulation Time (seconds)'),
            yaxis=dict(title='Pressure (m)'),
            hovermode='x unified'
        )
        
        return {'data': traces, 'layout': layout}
    
    def create_flow_trend(self):
        """Create flow trend chart"""
        if len(self.time_history) == 0:
            return {}
        
        # Plot trends for first few pipes
        pipe_indices = self.d.getLinkPipeIndex()
        traces = []
        for i in range(min(5, len(pipe_indices))):
            idx = pipe_indices[i] - 1
            traces.append(go.Scatter(
                x=list(self.time_history),
                y=list(self.flow_history[idx]),
                mode='lines',
                name=self.link_ids[idx]
            ))
        
        layout = go.Layout(
            title='Flow Trends',
            xaxis=dict(title='Simulation Time (seconds)'),
            yaxis=dict(title='Flow (LPS)'),
            hovermode='x unified'
        )
        
        return {'data': traces, 'layout': layout}
    
    def check_alerts(self):
        """Check for operational alerts"""
        if self.current_state is None:
            return []
        
        alerts = []
        pressures = self.current_state.get('pressures', [])
        
        min_pressure = 20  # Minimum required pressure in meters
        max_pressure = 100  # Maximum safe pressure in meters
        
        for i, p in enumerate(pressures):
            if p < min_pressure:
                alerts.append(
                    html.Div([
                        html.Span('⚠️ ', style={'fontSize': '20px'}),
                        f"Low pressure at {self.node_ids[i]}: {p:.2f} m"
                    ], style={'color': 'red', 'padding': '5px', 'marginBottom': '5px'})
                )
            elif p > max_pressure:
                alerts.append(
                    html.Div([
                        html.Span('⚠️ ', style={'fontSize': '20px'}),
                        f"High pressure at {self.node_ids[i]}: {p:.2f} m"
                    ], style={'color': 'orange', 'padding': '5px', 'marginBottom': '5px'})
                )
        
        if not alerts:
            return html.Div([
                html.Span('✅ ', style={'fontSize': '20px'}),
                'All systems normal'
            ], style={'color': 'green', 'fontWeight': 'bold', 'padding': '5px'})
        
        return alerts
    
    def generate_statistics(self):
        """Generate network statistics"""
        if self.current_state is None:
            return []
        
        pressures = self.current_state.get('pressures', [])
        flows = self.current_state.get('flows', [])
        demands = self.current_state.get('demands', [])
        
        stats = [
            html.Div(f"Avg Pressure: {np.mean(pressures):.2f} m", style={'padding': '3px'}),
            html.Div(f"Min Pressure: {np.min(pressures):.2f} m", style={'padding': '3px'}),
            html.Div(f"Max Pressure: {np.max(pressures):.2f} m", style={'padding': '3px'}),
            html.Hr(),
            html.Div(f"Total Flow: {np.sum(np.abs(flows)):.2f} LPS", style={'padding': '3px'}),
            html.Div(f"Total Demand: {np.sum(demands):.2f} LPS", style={'padding': '3px'}),
            html.Hr(),
            html.Div(f"Network Nodes: {self.d.getNodeCount()}", style={'padding': '3px'}),
            html.Div(f"Network Links: {self.d.getLinkCount()}", style={'padding': '3px'}),
        ]
        
        return stats
    
    def update_state(self, state):
        """Update dashboard with new state data"""
        self.current_state = state
        
        # Update history
        if 'time' in state:
            self.time_history.append(state['time'])
        
        if 'pressures' in state:
            for i, p in enumerate(state['pressures']):
                self.pressure_history[i].append(p)
        
        if 'flows' in state:
            for i, f in enumerate(state['flows']):
                self.flow_history[i].append(f)
    
    def run(self, debug: bool = False, port: int = 8050):
        """
        Start the dashboard server
        
        Args:
            debug: Enable debug mode
            port: Port number for the server
        """
        print(f"\n{'='*60}")
        print(f"🌊 Starting Water Network Dashboard")
        print(f"{'='*60}")
        print(f"Dashboard URL: http://localhost:{port}")
        print(f"Press Ctrl+C to stop the server")
        print(f"{'='*60}\n")
        
        # Dash 2.16+ deprecates run_server in favor of run
        self.app.run(debug=debug, port=port, host='0.0.0.0')
