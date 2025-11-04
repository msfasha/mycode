import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import {
  FiDroplet,
  FiActivity,
  FiAlertTriangle,
  FiTrendingUp,
  FiClock,
  FiRefreshCw
} from 'react-icons/fi';
import PressureChart from '../components/charts/PressureChart';
import FlowChart from '../components/charts/FlowChart';
import SystemStatus from '../components/SystemStatus';
import AlertList from '../components/AlertList';

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
  height: 100%;
`;

const DashboardHeader = styled.div`
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

const RefreshButton = styled.button`
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

  &:hover {
    background-color: ${props => props.theme.colors.background};
    border-color: ${props => props.theme.colors.primary};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const StatCard = styled.div`
  background-color: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
  transition: all 0.2s;

  &:hover {
    box-shadow: ${props => props.theme.shadows.md};
  }
`;

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const StatTitle = styled.h3`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.textSecondary};
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const StatIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.color + '20'};
  color: ${props => props.color};
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const StatChange = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  font-size: 0.875rem;
  color: ${props => props.positive 
    ? props.theme.colors.success 
    : props.theme.colors.error
  };
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background-color: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const ChartTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0 0 ${props => props.theme.spacing.lg} 0;
`;

const BottomGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: ${props => props.theme.spacing.lg};

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const Dashboard = ({ simulationData, alerts }) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate refresh delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    setLastUpdate(new Date());
    setIsRefreshing(false);
  };

  // Calculate stats from simulation data
  const getStats = () => {
    if (!simulationData) {
      return {
        totalDemand: 0,
        averagePressure: 0,
        totalFlow: 0,
        activeAlerts: alerts.length
      };
    }

    const { summary, nodes, links } = simulationData;
    
    return {
      totalDemand: summary?.totalDemand || 0,
      averagePressure: summary?.averagePressure || 0,
      totalFlow: summary?.totalFlow || 0,
      activeAlerts: alerts.length
    };
  };

  const stats = getStats();

  return (
    <DashboardContainer>
      <DashboardHeader>
        <Title>System Dashboard</Title>
        <RefreshButton onClick={handleRefresh} disabled={isRefreshing}>
          <FiRefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
          {isRefreshing ? 'Refreshing...' : 'Refresh'}
        </RefreshButton>
      </DashboardHeader>

      <StatsGrid>
        <StatCard>
          <StatHeader>
            <StatTitle>Total Demand</StatTitle>
            <StatIcon color="#3b82f6">
              <FiDroplet size={20} />
            </StatIcon>
          </StatHeader>
          <StatValue>{stats.totalDemand.toFixed(1)} GPM</StatValue>
          <StatChange positive={stats.totalDemand > 0}>
            <FiTrendingUp size={14} />
            {stats.totalDemand > 0 ? 'Active' : 'No Demand'}
          </StatChange>
        </StatCard>

        <StatCard>
          <StatHeader>
            <StatTitle>Average Pressure</StatTitle>
            <StatIcon color="#10b981">
              <FiActivity size={20} />
            </StatIcon>
          </StatHeader>
          <StatValue>{stats.averagePressure.toFixed(1)} PSI</StatValue>
          <StatChange positive={stats.averagePressure > 20}>
            <FiTrendingUp size={14} />
            {stats.averagePressure > 20 ? 'Good' : 'Low'}
          </StatChange>
        </StatCard>

        <StatCard>
          <StatHeader>
            <StatTitle>Total Flow</StatTitle>
            <StatIcon color="#8b5cf6">
              <FiActivity size={20} />
            </StatIcon>
          </StatHeader>
          <StatValue>{stats.totalFlow.toFixed(1)} GPM</StatValue>
          <StatChange positive={stats.totalFlow > 0}>
            <FiTrendingUp size={14} />
            {stats.totalFlow > 0 ? 'Flowing' : 'Stagnant'}
          </StatChange>
        </StatCard>

        <StatCard>
          <StatHeader>
            <StatTitle>Active Alerts</StatTitle>
            <StatIcon color={stats.activeAlerts > 0 ? "#ef4444" : "#10b981"}>
              <FiAlertTriangle size={20} />
            </StatIcon>
          </StatHeader>
          <StatValue>{stats.activeAlerts}</StatValue>
          <StatChange positive={stats.activeAlerts === 0}>
            <FiClock size={14} />
            {stats.activeAlerts === 0 ? 'All Clear' : 'Attention Needed'}
          </StatChange>
        </StatCard>
      </StatsGrid>

      <ChartsGrid>
        <ChartCard>
          <ChartTitle>Pressure Distribution</ChartTitle>
          <PressureChart data={simulationData} />
        </ChartCard>

        <ChartCard>
          <ChartTitle>Flow Rates</ChartTitle>
          <FlowChart data={simulationData} />
        </ChartCard>
      </ChartsGrid>

      <BottomGrid>
        <SystemStatus simulationData={simulationData} />
        <AlertList alerts={alerts} />
      </BottomGrid>
    </DashboardContainer>
  );
};

export default Dashboard;



