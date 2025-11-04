import React from 'react';
import styled from 'styled-components';
import { FiAlertTriangle, FiAlertCircle, FiInfo, FiX, FiCheckCircle } from 'react-icons/fi';

const AlertContainer = styled.div`
  background-color: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const AlertHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const AlertTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const AlertCount = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  border-radius: 12px;
  background-color: ${props => props.count > 0 
    ? props.theme.colors.error 
    : props.theme.colors.success
  };
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
`;

const AlertList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  max-height: 400px;
  overflow-y: auto;
`;

const AlertItem = styled.div`
  display: flex;
  align-items: flex-start;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => {
    switch (props.severity) {
      case 'critical':
        return props.theme.colors.error + '10';
      case 'warning':
        return props.theme.colors.warning + '10';
      case 'info':
        return props.theme.colors.primary + '10';
      default:
        return props.theme.colors.background;
    }
  }};
  border-left: 3px solid ${props => {
    switch (props.severity) {
      case 'critical':
        return props.theme.colors.error;
      case 'warning':
        return props.theme.colors.warning;
      case 'info':
        return props.theme.colors.primary;
      default:
        return props.theme.colors.secondary;
    }
  }};
`;

const AlertIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;
  color: ${props => {
    switch (props.severity) {
      case 'critical':
        return props.theme.colors.error;
      case 'warning':
        return props.theme.colors.warning;
      case 'info':
        return props.theme.colors.primary;
      default:
        return props.theme.colors.secondary;
    }
  }};
`;

const AlertContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const AlertMessage = styled.div`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
  line-height: 1.4;
`;

const AlertDetails = styled.div`
  font-size: 0.75rem;
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const AlertTime = styled.div`
  font-size: 0.75rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const AlertActions = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const ClearButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  border-radius: ${props => props.theme.borderRadius.sm};
  background-color: transparent;
  color: ${props => props.theme.colors.textSecondary};
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
  }
`;

const NoAlerts = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xl};
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
`;

const NoAlertsIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: ${props => props.theme.colors.success + '20'};
  color: ${props => props.theme.colors.success};
  margin-bottom: ${props => props.theme.spacing.md};
`;

const NoAlertsText = styled.div`
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const NoAlertsSubtext = styled.div`
  font-size: 0.75rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const AlertListComponent = ({ alerts, onClearAlert }) => {
  const getAlertIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <FiAlertTriangle size={16} />;
      case 'warning':
        return <FiAlertCircle size={16} />;
      case 'info':
        return <FiInfo size={16} />;
      default:
        return <FiInfo size={16} />;
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // Less than 1 minute
      return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
      return `${Math.floor(diff / 60000)}m ago`;
    } else if (diff < 86400000) { // Less than 1 day
      return `${Math.floor(diff / 3600000)}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (alerts.length === 0) {
    return (
      <AlertContainer>
        <AlertHeader>
          <AlertTitle>System Alerts</AlertTitle>
          <AlertCount count={0}>0</AlertCount>
        </AlertHeader>
        
        <NoAlerts>
          <NoAlertsIcon>
            <FiCheckCircle size={24} />
          </NoAlertsIcon>
          <NoAlertsText>All Clear</NoAlertsText>
          <NoAlertsSubtext>No active alerts</NoAlertsSubtext>
        </NoAlerts>
      </AlertContainer>
    );
  }

  return (
    <AlertContainer>
      <AlertHeader>
        <AlertTitle>System Alerts</AlertTitle>
        <AlertCount count={alerts.length}>{alerts.length}</AlertCount>
      </AlertHeader>
      
      <AlertList>
        {alerts.map((alert, index) => (
          <AlertItem key={alert.id || index} severity={alert.severity}>
            <AlertIcon severity={alert.severity}>
              {getAlertIcon(alert.severity)}
            </AlertIcon>
            
            <AlertContent>
              <AlertMessage>{alert.message}</AlertMessage>
              {alert.nodeId && (
                <AlertDetails>Node: {alert.nodeId}</AlertDetails>
              )}
              {alert.linkId && (
                <AlertDetails>Link: {alert.linkId}</AlertDetails>
              )}
              {alert.value && (
                <AlertDetails>Value: {alert.value}</AlertDetails>
              )}
              <AlertTime>{formatTime(alert.timestamp)}</AlertTime>
            </AlertContent>
            
            <AlertActions>
              <ClearButton onClick={() => onClearAlert(alert.id || index)}>
                <FiX size={14} />
              </ClearButton>
            </AlertActions>
          </AlertItem>
        ))}
      </AlertList>
    </AlertContainer>
  );
};

export default AlertList;

