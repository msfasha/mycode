import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import styled from 'styled-components';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const MapContainerStyled = styled.div`
  width: 100%;
  height: 100vh;
  position: relative;
`;

const MapControls = styled.div`
  position: absolute;
  top: ${props => props.theme.spacing.lg};
  right: ${props => props.theme.spacing.lg};
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
`;

const ControlButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  box-shadow: ${props => props.theme.shadows.md};

  &:hover {
    background-color: ${props => props.theme.colors.background};
    border-color: ${props => props.theme.colors.primary};
  }

  &.active {
    background-color: ${props => props.theme.colors.primary};
    color: white;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const Legend = styled.div`
  position: absolute;
  bottom: ${props => props.theme.spacing.lg};
  left: ${props => props.theme.spacing.lg};
  z-index: 1000;
  background-color: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.md};
  min-width: 200px;
`;

const LegendTitle = styled.h4`
  font-size: 1rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0 0 ${props => props.theme.spacing.md} 0;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.sm};
  font-size: 0.875rem;
`;

const LegendColor = styled.div`
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: ${props => props.color};
  border: 2px solid white;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
`;

const LegendText = styled.span`
  color: ${props => props.theme.colors.text};
`;

const NetworkMap = ({ simulationData }) => {
  const [viewMode, setViewMode] = useState('pressure');
  const [showLegend, setShowLegend] = useState(true);

  // Default coordinates for the sample network
  const defaultCenter = [40.7128, -74.0060]; // New York City
  const defaultZoom = 13;

  // Generate network coordinates (simplified for demo)
  const getNetworkCoordinates = () => {
    const baseLat = 40.7128;
    const baseLng = -74.0060;
    
    return {
      nodes: {
        'J1': [baseLat + 0.01, baseLng + 0.01],
        'J2': [baseLat + 0.01, baseLng + 0.02],
        'J3': [baseLat + 0.01, baseLng + 0.03],
        'J4': [baseLat + 0.01, baseLng + 0.04],
        'R1': [baseLat, baseLng],
        'T1': [baseLat + 0.01, baseLng + 0.05]
      },
      links: [
        { from: 'R1', to: 'J1', id: 'P1' },
        { from: 'J1', to: 'J2', id: 'P2' },
        { from: 'J2', to: 'J3', id: 'P3' },
        { from: 'J3', to: 'J4', id: 'P4' },
        { from: 'J4', to: 'T1', id: 'P5' }
      ]
    };
  };

  const getNodeColor = (nodeId, nodeData) => {
    if (!nodeData) return '#64748b';
    
    const pressure = nodeData.pressure || 0;
    if (pressure > 40) return '#10b981'; // Green - Good pressure
    if (pressure > 20) return '#f59e0b'; // Yellow - Moderate pressure
    if (pressure > 10) return '#f97316'; // Orange - Low pressure
    return '#ef4444'; // Red - Very low pressure
  };

  const getNodeSize = (nodeData) => {
    if (!nodeData) return 8;
    
    const demand = nodeData.demand || 0;
    return Math.max(8, Math.min(20, 8 + (demand / 10)));
  };

  const getLinkColor = (linkId, linkData) => {
    if (!linkData) return '#64748b';
    
    const flow = Math.abs(linkData.flow || 0);
    if (flow > 50) return '#3b82f6'; // Blue - High flow
    if (flow > 20) return '#8b5cf6'; // Purple - Medium flow
    if (flow > 5) return '#06b6d4'; // Cyan - Low flow
    return '#64748b'; // Gray - No flow
  };

  const getLinkWidth = (linkData) => {
    if (!linkData) return 2;
    
    const flow = Math.abs(linkData.flow || 0);
    return Math.max(2, Math.min(8, 2 + (flow / 10)));
  };

  const network = getNetworkCoordinates();
  const { nodes: nodeCoords, links: linkCoords } = network;

  const renderNodes = () => {
    if (!simulationData?.nodes) return null;

    return Object.entries(simulationData.nodes).map(([nodeId, nodeData]) => {
      const coords = nodeCoords[nodeId];
      if (!coords) return null;

      return (
        <CircleMarker
          key={nodeId}
          center={coords}
          radius={getNodeSize(nodeData)}
          fillColor={getNodeColor(nodeId, nodeData)}
          color="white"
          weight={2}
          opacity={1}
          fillOpacity={0.8}
        >
          <Popup>
            <div>
              <h4>{nodeId}</h4>
              <p><strong>Type:</strong> {nodeData.type}</p>
              <p><strong>Pressure:</strong> {nodeData.pressure?.toFixed(1)} PSI</p>
              <p><strong>Head:</strong> {nodeData.head?.toFixed(1)} ft</p>
              <p><strong>Demand:</strong> {nodeData.demand?.toFixed(1)} GPM</p>
              {nodeData.tankLevel && (
                <p><strong>Tank Level:</strong> {nodeData.tankLevel?.toFixed(1)} ft</p>
              )}
            </div>
          </Popup>
        </CircleMarker>
      );
    });
  };

  const renderLinks = () => {
    if (!simulationData?.links) return null;

    return linkCoords.map((link) => {
      const fromCoords = nodeCoords[link.from];
      const toCoords = nodeCoords[link.to];
      const linkData = simulationData.links[link.id];

      if (!fromCoords || !toCoords) return null;

      return (
        <Polyline
          key={link.id}
          positions={[fromCoords, toCoords]}
          color={getLinkColor(link.id, linkData)}
          weight={getLinkWidth(linkData)}
          opacity={0.8}
        >
          <Popup>
            <div>
              <h4>{link.id}</h4>
              <p><strong>Type:</strong> {linkData?.type}</p>
              <p><strong>Flow:</strong> {linkData?.flow?.toFixed(1)} GPM</p>
              <p><strong>Velocity:</strong> {linkData?.velocity?.toFixed(1)} ft/s</p>
              <p><strong>Headloss:</strong> {linkData?.headloss?.toFixed(1)} ft</p>
              <p><strong>Status:</strong> {linkData?.status ? 'Open' : 'Closed'}</p>
            </div>
          </Popup>
        </Polyline>
      );
    });
  };

  return (
    <MapContainerStyled>
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {renderLinks()}
        {renderNodes()}
      </MapContainer>

      <MapControls>
        <ControlButton
          className={viewMode === 'pressure' ? 'active' : ''}
          onClick={() => setViewMode('pressure')}
        >
          Pressure View
        </ControlButton>
        <ControlButton
          className={viewMode === 'flow' ? 'active' : ''}
          onClick={() => setViewMode('flow')}
        >
          Flow View
        </ControlButton>
        <ControlButton
          className={viewMode === 'demand' ? 'active' : ''}
          onClick={() => setViewMode('demand')}
        >
          Demand View
        </ControlButton>
        <ControlButton
          onClick={() => setShowLegend(!showLegend)}
        >
          {showLegend ? 'Hide' : 'Show'} Legend
        </ControlButton>
      </MapControls>

      {showLegend && (
        <Legend>
          <LegendTitle>Network Legend</LegendTitle>
          
          <LegendItem>
            <LegendColor color="#10b981" />
            <LegendText>High Pressure (&gt;40 PSI)</LegendText>
          </LegendItem>
          
          <LegendItem>
            <LegendColor color="#f59e0b" />
            <LegendText>Good Pressure (20-40 PSI)</LegendText>
          </LegendItem>
          
          <LegendItem>
            <LegendColor color="#f97316" />
            <LegendText>Low Pressure (10-20 PSI)</LegendText>
          </LegendItem>
          
          <LegendItem>
            <LegendColor color="#ef4444" />
            <LegendText>Critical Pressure (&lt;10 PSI)</LegendText>
          </LegendItem>
          
          <LegendItem>
            <LegendColor color="#3b82f6" />
            <LegendText>High Flow</LegendText>
          </LegendItem>
          
          <LegendItem>
            <LegendColor color="#64748b" />
            <LegendText>No Flow</LegendText>
          </LegendItem>
        </Legend>
      )}
    </MapContainerStyled>
  );
};

export default NetworkMap;



