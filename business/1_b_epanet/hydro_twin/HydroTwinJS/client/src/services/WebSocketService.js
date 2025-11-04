class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
    this.listeners = {
      connect: [],
      disconnect: [],
      simulationResults: [],
      alert: [],
      error: []
    };
  }

  connect() {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.hostname}:3002/ws`;
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('🔌 WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connect');
        
        // Subscribe to simulation results and alerts
        this.send({
          type: 'subscribe',
          subscriptions: ['simulation_results', 'alerts']
        });
      };
      
      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        this.emit('disconnect');
        this.handleReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.emit('error', error);
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('❌ Failed to parse WebSocket message:', error);
        }
      };
      
    } catch (error) {
      console.error('❌ Failed to connect WebSocket:', error);
      this.emit('error', error);
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    } else {
      console.error('❌ Max reconnection attempts reached');
    }
  }

  handleMessage(data) {
    switch (data.type) {
      case 'simulation_results':
        this.emit('simulationResults', data.data);
        break;
      case 'alert':
        this.emit('alert', data.data);
        break;
      case 'connection':
        console.log('📨 Server message:', data.message);
        break;
      case 'error':
        console.error('❌ Server error:', data.message);
        this.emit('error', new Error(data.message));
        break;
      default:
        console.log('📨 Unknown message type:', data.type);
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message');
    }
  }

  onConnect(callback) {
    this.listeners.connect.push(callback);
  }

  onDisconnect(callback) {
    this.listeners.disconnect.push(callback);
  }

  onSimulationResults(callback) {
    this.listeners.simulationResults.push(callback);
  }

  onAlert(callback) {
    this.listeners.alert.push(callback);
  }

  onError(callback) {
    this.listeners.error.push(callback);
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  getConnectionStatus() {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }
}

export { WebSocketService };



