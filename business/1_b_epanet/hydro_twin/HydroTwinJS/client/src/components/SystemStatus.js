import React from 'react';
import styled from 'styled-components';
import { FiCheckCircle, FiXCircle, FiAlertCircle, FiActivity } from 'react-icons/fi';

const StatusContainer = styled.div`
  background-color: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const StatusHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const StatusTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const StatusIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.color + '20'};
  color: ${props => props.color};
`;

const StatusGrid = styled.div`
  display: grid;
  gap: ${props => props.theme.spacing.md};
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.sm} 0;
  border-bottom: 1px solid ${props => props.theme.colors.border};
`;

const StatusItemLast = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.sm} 0;
`;

const StatusLabel = styled.span`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const StatusValue = styled.span`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.text};
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const Indicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: ${props => {
    switch (props.status) {
      case 'good':
        return props.theme.colors.success;
      case 'warning':
        return props.theme.colors.warning;
      case 'error':
        return props.theme.colors.error;
      default:
        return props.theme.colors.secondary;
    }
  }};
`;

const SystemStatus = ({ simulationData }) => {
  const getSystemStatus = () => {
    if (!simulationData) {
      return {
        overall: 'unknown',
        nodes: 0,
        links: 0,
        averagePressure: 0,
        totalDemand: 0,
        lastUpdate: 'Never'
      };
    }

    const { summary, nodes, links } = simulationData;
    const nodeCount = Object.keys(nodes || {}).length;
    const linkCount = Object.keys(links || {}).length;
    const avgPressure = summary?.averagePressure || 0;
    const totalDemand = summary?.totalDemand || 0;

    let overallStatus = 'good';
    if (avgPressure < 20) overallStatus = 'warning';
    if (avgPressure < 10) overallStatus = 'error';

    return {
      overall: overallStatus,
      nodes: nodeCount,
      links: linkCount,
      averagePressure: avgPressure,
      totalDemand: totalDemand,
      lastUpdate: new Date().toLocaleTimeString()
    };
  };

  const status = getSystemStatus();

  const getStatusIcon = () => {
    switch (status.overall) {
      case 'good':
        return <FiCheckCircle size={20} />;
      case 'warning':
        return <FiAlertCircle size={20} />;
      case 'error':
        return <FiXCircle size={20} />;
      default:
        return <FiActivity size={20} />;
    }
  };

  const getStatusColor = () => {
    switch (status.overall) {
      case 'good':
        return '#10b981';
      case 'warning':
        return '#f59e0b';
      case 'error':
        return '#ef4444';
      default:
        return '#64748b';
    }
  };

  return (
    <StatusContainer>
      <StatusHeader>
        <StatusIcon color={getStatusColor()}>
          {getStatusIcon()}
        </StatusIcon>
        <StatusTitle>System Status</StatusTitle>
      </StatusHeader>

      <StatusGrid>
        <StatusItem>
          <StatusLabel>Overall Status</StatusLabel>
          <StatusIndicator>
            <Indicator status={status.overall} />
            <StatusValue>
              {status.overall === 'good' ? 'Operational' : 
               status.overall === 'warning' ? 'Warning' : 
               status.overall === 'error' ? 'Critical' : 'Unknown'}
            </StatusValue>
          </StatusIndicator>
        </StatusItem>

        <StatusItem>
          <StatusLabel>Network Nodes</StatusLabel>
          <StatusValue>{status.nodes}</StatusValue>
        </StatusItem>

        <StatusItem>
          <StatusLabel>Network Links</StatusLabel>
          <StatusValue>{status.links}</StatusValue>
        </StatusItem>

        <StatusItem>
          <StatusLabel>Average Pressure</StatusLabel>
          <StatusValue>{status.averagePressure.toFixed(1)} PSI</StatusValue>
        </StatusItem>

        <StatusItem>
          <StatusLabel>Total Demand</StatusLabel>
          <StatusValue>{status.totalDemand.toFixed(1)} GPM</StatusValue>
        </StatusItem>

        <StatusItemLast>
          <StatusLabel>Last Update</StatusLabel>
          <StatusValue>{status.lastUpdate}</StatusValue>
        </StatusItemLast>
      </StatusGrid>
    </StatusContainer>
  );
};

export default SystemStatus;



