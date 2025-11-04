import { useState, useEffect } from 'react';
import { useNetwork } from '../context/NetworkContext';

const API_BASE = 'http://localhost:8000';

export function SimulatorPage() {
  const { network, networkFile, networkId: contextNetworkId, setNetworkId } = useNetwork();
  const [simulationStatus, setSimulationStatus] = useState<'idle' | 'running' | 'stopping'>('idle');
  const [networkId, setLocalNetworkId] = useState<string | null>(contextNetworkId);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // Sync local networkId with context
  useEffect(() => {
    if (contextNetworkId) {
      setLocalNetworkId(contextNetworkId);
    }
  }, [contextNetworkId]);

  // Check actual backend status when component mounts or networkId changes
  useEffect(() => {
    if (networkId) {
      checkSimulationStatus(networkId);
    }
  }, [networkId]);

  const checkSimulationStatus = async (id: string) => {
    if (!id) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/simulation/status/${id}`);
      const data = await response.json();
      setSimulationStatus(prevStatus => {
        if (data.running && prevStatus !== 'running') {
          setMessage('Simulation is running');
          return 'running';
        } else if (!data.running && prevStatus === 'running') {
          setMessage('Simulation stopped');
          return 'idle';
        }
        return prevStatus;
      });
    } catch (err) {
      console.error('Error checking status:', err);
    }
  };

  useEffect(() => {
    // Check simulation status periodically if we have a networkId
    if (networkId) {
      const interval = setInterval(() => checkSimulationStatus(networkId), 5000);
      return () => clearInterval(interval);
    }
  }, [networkId]);

  const startSimulation = async () => {
    if (!network || !networkFile) {
      setError('Please load a network file first on the Network View page');
      return;
    }

    setError(null);
    setMessage('Starting simulation...');

    try {
      // 1. Upload network to backend
      const formData = new FormData();
      formData.append('file', networkFile);
      
      setMessage('Uploading network to backend...');
      const uploadResponse = await fetch(`${API_BASE}/api/network/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!uploadResponse.ok) {
        throw new Error('Failed to upload network');
      }
      
      const uploadData = await uploadResponse.json();
      const id = uploadData.network_id;
      setLocalNetworkId(id);
      setNetworkId(id); // Store in context for persistence

      // 2. Establish baseline
      setMessage('Establishing baseline...');
      const baselineResponse = await fetch(`${API_BASE}/api/network/${id}/baseline`, {
        method: 'POST'
      });
      
      if (!baselineResponse.ok) {
        throw new Error('Failed to establish baseline');
      }

      // 3. Start simulation
      setMessage('Starting simulation...');
      const simResponse = await fetch(`${API_BASE}/api/simulation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ network_id: id })
      });
      
      if (!simResponse.ok) {
        throw new Error('Failed to start simulation');
      }
      
      const simData = await simResponse.json();
      
      if (simData.success) {
        setSimulationStatus('running');
        setMessage('Simulation running. Data is being generated and stored in database.');
        setError(null);
      } else {
        throw new Error('Simulation failed to start');
      }
    } catch (err: any) {
      setError(`Failed to start simulation: ${err.message}`);
      setMessage(null);
      setSimulationStatus('idle');
    }
  };

  const stopSimulation = async () => {
    if (!networkId) return;
    
    setMessage('Stopping simulation...');
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/simulation/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ network_id: networkId })
      });
      
      if (!response.ok) {
        throw new Error('Failed to stop simulation');
      }
      
      const data = await response.json();
      if (data.success) {
        setSimulationStatus('idle');
        setMessage('Simulation stopped');
        // Optionally clear networkId from context when stopped
        // setNetworkId(null);
      }
    } catch (err: any) {
      setError(`Failed to stop simulation: ${err.message}`);
    }
  };

  return (
    <div className="simulator-page">
      <h2>SCADA Simulator</h2>
      
      {!network && (
        <div className="warning-box">
          <strong>⚠️ No network loaded</strong>
          <p>Please upload a network file on the Network View page first.</p>
        </div>
      )}
      
      {network && (
        <div className="simulator-controls">
          <div className="network-info">
            <p><strong>Network:</strong> {network.title || 'Loaded network'}</p>
            <p><strong>Junctions:</strong> {network.junctions.length}</p>
            <p><strong>Status:</strong> {simulationStatus}</p>
          </div>
          
          <div className="button-group">
            <button 
              onClick={startSimulation}
              disabled={simulationStatus === 'running'}
              className="btn-primary"
            >
              Start Simulation
            </button>
            
            <button 
              onClick={stopSimulation}
              disabled={simulationStatus !== 'running'}
              className="btn-secondary"
            >
              Stop Simulation
            </button>
          </div>
          
          {message && (
            <div className="message-box">
              {message}
            </div>
          )}
        </div>
      )}
      
      {error && (
        <div className="error-box">
          {error}
        </div>
      )}
      
      <style>{`
        .simulator-page {
          padding: 2rem;
          max-width: 800px;
          margin: 0 auto;
        }
        
        .warning-box {
          background-color: #fff3cd;
          border: 1px solid #ffc107;
          border-radius: 8px;
          padding: 1.5rem;
          margin-bottom: 2rem;
        }
        
        .simulator-controls {
          background: white;
          border-radius: 8px;
          padding: 2rem;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .network-info {
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #dee2e6;
        }
        
        .network-info p {
          margin: 0.5rem 0;
        }
        
        .button-group {
          display: flex;
          gap: 1rem;
          margin-bottom: 1rem;
        }
        
        .btn-primary, .btn-secondary {
          padding: 0.75rem 2rem;
          border: none;
          border-radius: 4px;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.3s;
        }
        
        .btn-primary {
          background-color: #007bff;
          color: white;
        }
        
        .btn-primary:hover:not(:disabled) {
          background-color: #0056b3;
        }
        
        .btn-primary:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }
        
        .btn-secondary {
          background-color: #dc3545;
          color: white;
        }
        
        .btn-secondary:hover:not(:disabled) {
          background-color: #c82333;
        }
        
        .btn-secondary:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }
        
        .message-box {
          background-color: #d4edda;
          border: 1px solid #c3e6cb;
          color: #155724;
          padding: 1rem;
          border-radius: 4px;
          margin-top: 1rem;
        }
        
        .error-box {
          background-color: #f8d7da;
          border: 1px solid #f5c6cb;
          color: #721c24;
          padding: 1rem;
          border-radius: 4px;
          margin-top: 1rem;
        }
      `}</style>
    </div>
  );
}



