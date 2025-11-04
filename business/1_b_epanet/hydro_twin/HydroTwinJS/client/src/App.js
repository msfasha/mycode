import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import { WebSocketService } from './services/WebSocketService';
import { ApiService } from './services/ApiService';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import NetworkMap from './pages/NetworkMap';
import Analytics from './pages/Analytics';
import Alerts from './pages/Alerts';
import Settings from './pages/Settings';

const theme = {
  colors: {
    primary: '#2563eb',
    secondary: '#64748b',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    background: '#f8fafc',
    surface: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: '#e2e8f0'
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    xxl: '3rem'
  },
  borderRadius: {
    sm: '0.25rem',
    md: '0.5rem',
    lg: '0.75rem'
  },
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)'
  }
};

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
  }

  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
      monospace;
  }

  .leaflet-container {
    height: 100%;
    width: 100%;
  }
`;

const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  background-color: ${props => props.theme.colors.background};
`;

const MainContent = styled.main`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const ContentArea = styled.div`
  flex: 1;
  padding: ${props => props.theme.spacing.lg};
  overflow-y: auto;
  background-color: ${props => props.theme.colors.background};
`;

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [simulationData, setSimulationData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('connecting');

  useEffect(() => {
    // Initialize WebSocket connection
    const wsService = new WebSocketService();
    
    wsService.onConnect(() => {
      setConnectionStatus('connected');
      console.log('🔌 Connected to HydroTwinJS server');
    });

    wsService.onDisconnect(() => {
      setConnectionStatus('disconnected');
      console.log('🔌 Disconnected from server');
    });

    wsService.onSimulationResults((data) => {
      setSimulationData(data);
      console.log('📊 Received simulation results:', data);
    });

    wsService.onAlert((alert) => {
      setAlerts(prev => [alert, ...prev.slice(0, 9)]); // Keep last 10 alerts
      console.log('🚨 Received alert:', alert);
    });

    // Initialize API service
    const apiService = new ApiService();
    
    // Load initial data
    const loadInitialData = async () => {
      try {
        const [summary, alertsData] = await Promise.all([
          apiService.getSimulationSummary(),
          apiService.getAlerts()
        ]);
        
        setAlerts(alertsData);
        console.log('📈 Initial data loaded');
      } catch (error) {
        console.error('❌ Failed to load initial data:', error);
      }
    };

    loadInitialData();

    return () => {
      wsService.disconnect();
    };
  }, []);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Router>
        <AppContainer>
          <Sidebar isOpen={sidebarOpen} />
          <MainContent>
            <Header 
              onToggleSidebar={toggleSidebar}
              connectionStatus={connectionStatus}
              alertsCount={alerts.length}
            />
            <ContentArea>
              <Routes>
                <Route 
                  path="/" 
                  element={
                    <Dashboard 
                      simulationData={simulationData}
                      alerts={alerts}
                    />
                  } 
                />
                <Route 
                  path="/network" 
                  element={
                    <NetworkMap 
                      simulationData={simulationData}
                    />
                  } 
                />
                <Route 
                  path="/analytics" 
                  element={
                    <Analytics 
                      simulationData={simulationData}
                    />
                  } 
                />
                <Route 
                  path="/alerts" 
                  element={
                    <Alerts 
                      alerts={alerts}
                      onClearAlert={(id) => {
                        setAlerts(prev => prev.filter(alert => alert.id !== id));
                      }}
                    />
                  } 
                />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </ContentArea>
          </MainContent>
        </AppContainer>
      </Router>
    </ThemeProvider>
  );
}

export default App;



