const WebSocket = require('ws');

class WebSocketService {
  constructor(server) {
    this.wss = new WebSocket.Server({ 
      server,
      path: '/ws'
    });
    
    this.clients = new Set();
    this.setupWebSocketServer();
  }

  setupWebSocketServer() {
    this.wss.on('connection', (ws, req) => {
      console.log('🔌 New WebSocket client connected');
      
      // Add client to set
      this.clients.add(ws);
      
      // Send welcome message
      this.sendToClient(ws, {
        type: 'connection',
        message: 'Connected to HydroTwinJS real-time simulation',
        timestamp: new Date().toISOString()
      });

      // Handle client messages
      ws.on('message', (message) => {
        try {
          const data = JSON.parse(message);
          this.handleClientMessage(ws, data);
        } catch (error) {
          console.error('❌ Invalid WebSocket message:', error);
          this.sendToClient(ws, {
            type: 'error',
            message: 'Invalid message format'
          });
        }
      });

      // Handle client disconnect
      ws.on('close', () => {
        console.log('🔌 WebSocket client disconnected');
        this.clients.delete(ws);
      });

      // Handle errors
      ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error);
        this.clients.delete(ws);
      });
    });

    console.log('🌐 WebSocket server ready');
  }

  handleClientMessage(ws, data) {
    switch (data.type) {
      case 'subscribe':
        this.handleSubscription(ws, data);
        break;
      case 'request_data':
        this.handleDataRequest(ws, data);
        break;
      case 'ping':
        this.sendToClient(ws, { type: 'pong', timestamp: new Date().toISOString() });
        break;
      default:
        console.log('📨 Unknown message type:', data.type);
    }
  }

  handleSubscription(ws, data) {
    // Store subscription preferences for this client
    ws.subscriptions = data.subscriptions || ['simulation_results', 'alerts'];
    
    this.sendToClient(ws, {
      type: 'subscription_confirmed',
      subscriptions: ws.subscriptions,
      timestamp: new Date().toISOString()
    });
  }

  handleDataRequest(ws, data) {
    // Handle specific data requests from clients
    switch (data.request) {
      case 'historical_data':
        // This would typically fetch from database
        this.sendToClient(ws, {
          type: 'historical_data',
          data: [],
          message: 'Historical data request received'
        });
        break;
      case 'network_status':
        this.sendToClient(ws, {
          type: 'network_status',
          status: 'operational',
          timestamp: new Date().toISOString()
        });
        break;
      default:
        this.sendToClient(ws, {
          type: 'error',
          message: 'Unknown data request'
        });
    }
  }

  sendToClient(ws, data) {
    if (ws.readyState === WebSocket.OPEN) {
      try {
        ws.send(JSON.stringify(data));
      } catch (error) {
        console.error('❌ Failed to send message to client:', error);
        this.clients.delete(ws);
      }
    }
  }

  broadcastResults(results) {
    const message = {
      type: 'simulation_results',
      data: results,
      timestamp: new Date().toISOString()
    };

    this.broadcast(message);
  }

  broadcastAlert(alert) {
    const message = {
      type: 'alert',
      data: alert,
      timestamp: new Date().toISOString()
    };

    this.broadcast(message);
  }

  broadcastStatus(status) {
    const message = {
      type: 'status_update',
      data: status,
      timestamp: new Date().toISOString()
    };

    this.broadcast(message);
  }

  broadcast(message) {
    const deadClients = [];
    
    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        try {
          client.send(JSON.stringify(message));
        } catch (error) {
          console.error('❌ Failed to broadcast to client:', error);
          deadClients.push(client);
        }
      } else {
        deadClients.push(client);
      }
    });

    // Clean up dead clients
    deadClients.forEach(client => this.clients.delete(client));
    
    console.log(`📡 Broadcasted to ${this.clients.size} clients`);
  }

  getConnectedClientsCount() {
    return this.clients.size;
  }

  getClientInfo() {
    return Array.from(this.clients).map(ws => ({
      readyState: ws.readyState,
      subscriptions: ws.subscriptions || [],
      connected: ws.readyState === WebSocket.OPEN
    }));
  }
}

module.exports = WebSocketService;
