import React, { useState } from 'react';
import styled from 'styled-components';
import { FiAlertTriangle, FiAlertCircle, FiInfo, FiX, FiFilter, FiSearch } from 'react-icons/fi';

const AlertsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
  height: 100%;
`;

const AlertsHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const Title = styled.h2`
  font-size: 1.875rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const Controls = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const SearchInput = styled.input`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;
  width: 200px;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const FilterSelect = styled.select`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const AlertsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.md};
  flex: 1;
  overflow-y: auto;
`;

const AlertCard = styled.div`
  background-color: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-left: 4px solid ${props => {
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
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
  transition: all 0.2s;

  &:hover {
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const AlertHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const AlertTitle = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const AlertIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: ${props => {
    switch (props.severity) {
      case 'critical':
        return props.theme.colors.error + '20';
      case 'warning':
        return props.theme.colors.warning + '20';
      case 'info':
        return props.theme.colors.primary + '20';
      default:
        return props.theme.colors.secondary + '20';
    }
  }};
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

const AlertMessage = styled.div`
  font-size: 1rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const AlertSeverity = styled.span`
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  background-color: ${props => {
    switch (props.severity) {
      case 'critical':
        return props.theme.colors.error + '20';
      case 'warning':
        return props.theme.colors.warning + '20';
      case 'info':
        return props.theme.colors.primary + '20';
      default:
        return props.theme.colors.secondary + '20';
    }
  }};
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
  margin-bottom: ${props => props.theme.spacing.md};
`;

const AlertDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const DetailItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
`;

const DetailLabel = styled.span`
  font-size: 0.75rem;
  font-weight: 500;
  color: ${props => props.theme.colors.textSecondary};
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const DetailValue = styled.span`
  font-size: 0.875rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const AlertFooter = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: ${props => props.theme.spacing.sm};
  border-top: 1px solid ${props => props.theme.colors.border};
`;

const AlertTime = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const AlertActions = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.sm};
  background-color: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.75rem;

  &:hover {
    background-color: ${props => props.theme.colors.background};
    border-color: ${props => props.theme.colors.primary};
  }
`;

const ClearButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: transparent;
  color: ${props => props.theme.colors.textSecondary};
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background-color: ${props => props.theme.colors.error + '20'};
    color: ${props => props.theme.colors.error};
  }
`;

const NoAlerts = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.theme.spacing.xxl};
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
`;

const NoAlertsIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: ${props => props.theme.colors.success + '20'};
  color: ${props => props.theme.colors.success};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const NoAlertsText = styled.div`
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.text};
`;

const NoAlertsSubtext = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
`;

const Alerts = ({ alerts, onClearAlert }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');

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

  const filteredAlerts = alerts.filter(alert => {
    const matchesSearch = alert.message.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === 'all' || alert.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  if (alerts.length === 0) {
    return (
      <AlertsContainer>
        <AlertsHeader>
          <Title>System Alerts</Title>
        </AlertsHeader>
        
        <NoAlerts>
          <NoAlertsIcon>
            <FiAlertTriangle size={32} />
          </NoAlertsIcon>
          <NoAlertsText>No Alerts</NoAlertsText>
          <NoAlertsSubtext>All systems are operating normally</NoAlertsSubtext>
        </NoAlerts>
      </AlertsContainer>
    );
  }

  return (
    <AlertsContainer>
      <AlertsHeader>
        <Title>System Alerts</Title>
        <Controls>
          <SearchInput
            type="text"
            placeholder="Search alerts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <FilterSelect
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </FilterSelect>
        </Controls>
      </AlertsHeader>

      <AlertsList>
        {filteredAlerts.map((alert, index) => (
          <AlertCard key={alert.id || index} severity={alert.severity}>
            <AlertHeader>
              <AlertTitle>
                <AlertIcon severity={alert.severity}>
                  {getAlertIcon(alert.severity)}
                </AlertIcon>
                <AlertMessage>{alert.message}</AlertMessage>
              </AlertTitle>
              <AlertSeverity severity={alert.severity}>
                {alert.severity}
              </AlertSeverity>
            </AlertHeader>

            <AlertContent>
              <AlertDetails>
                {alert.nodeId && (
                  <DetailItem>
                    <DetailLabel>Node</DetailLabel>
                    <DetailValue>{alert.nodeId}</DetailValue>
                  </DetailItem>
                )}
                {alert.linkId && (
                  <DetailItem>
                    <DetailLabel>Link</DetailLabel>
                    <DetailValue>{alert.linkId}</DetailValue>
                  </DetailItem>
                )}
                {alert.value && (
                  <DetailItem>
                    <DetailLabel>Value</DetailLabel>
                    <DetailValue>{alert.value}</DetailValue>
                  </DetailItem>
                )}
                {alert.threshold && (
                  <DetailItem>
                    <DetailLabel>Threshold</DetailLabel>
                    <DetailValue>{alert.threshold}</DetailValue>
                  </DetailItem>
                )}
              </AlertDetails>
            </AlertContent>

            <AlertFooter>
              <AlertTime>{formatTime(alert.timestamp)}</AlertTime>
              <AlertActions>
                <ActionButton>
                  Acknowledge
                </ActionButton>
                <ClearButton onClick={() => onClearAlert(alert.id || index)}>
                  <FiX size={16} />
                </ClearButton>
              </AlertActions>
            </AlertFooter>
          </AlertCard>
        ))}
      </AlertsList>
    </AlertsContainer>
  );
};

export default Alerts;



