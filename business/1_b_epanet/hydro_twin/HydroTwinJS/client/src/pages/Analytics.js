import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { FiTrendingUp, FiBarChart2, FiPieChart, FiDownload } from 'react-icons/fi';

const AnalyticsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
  height: 100%;
`;

const AnalyticsHeader = styled.div`
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

const ExportButton = styled.button`
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
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};

  @media (max-width: 1024px) {
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
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const ChartContainer = styled.div`
  width: 100%;
  height: 300px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const StatCard = styled.div`
  background-color: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const StatTitle = styled.h4`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.textSecondary};
  margin: 0 0 ${props => props.theme.spacing.sm} 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const StatChange = styled.div`
  font-size: 0.875rem;
  color: ${props => props.positive ? props.theme.colors.success : props.theme.colors.error};
`;

const Analytics = ({ simulationData }) => {
  const [timeRange, setTimeRange] = useState('24h');
  const [chartData, setChartData] = useState([]);

  // Generate mock historical data
  useEffect(() => {
    const generateHistoricalData = () => {
      const data = [];
      const now = new Date();
      
      for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        const baseDemand = 100 + Math.sin(i * Math.PI / 12) * 50;
        const basePressure = 30 + Math.sin(i * Math.PI / 12) * 10;
        
        data.push({
          time: time.toISOString(),
          hour: time.getHours(),
          demand: baseDemand + Math.random() * 20 - 10,
          pressure: basePressure + Math.random() * 5 - 2.5,
          flow: baseDemand * 0.8 + Math.random() * 10 - 5
        });
      }
      
      return data;
    };

    setChartData(generateHistoricalData());
  }, [timeRange]);

  // Calculate analytics from simulation data
  const getAnalytics = () => {
    if (!simulationData) {
      return {
        totalNodes: 0,
        totalLinks: 0,
        averagePressure: 0,
        totalDemand: 0,
        maxPressure: 0,
        minPressure: 0,
        pressureVariance: 0
      };
    }

    const { nodes, links, summary } = simulationData;
    const nodeCount = Object.keys(nodes || {}).length;
    const linkCount = Object.keys(links || {}).length;
    
    const pressures = Object.values(nodes || {})
      .map(node => node.pressure || 0)
      .filter(p => p > 0);
    
    const averagePressure = pressures.length > 0 
      ? pressures.reduce((sum, p) => sum + p, 0) / pressures.length 
      : 0;
    
    const maxPressure = Math.max(...pressures, 0);
    const minPressure = Math.min(...pressures, 0);
    const pressureVariance = pressures.length > 0
      ? pressures.reduce((sum, p) => sum + Math.pow(p - averagePressure, 2), 0) / pressures.length
      : 0;

    return {
      totalNodes: nodeCount,
      totalLinks: linkCount,
      averagePressure: averagePressure,
      totalDemand: summary?.totalDemand || 0,
      maxPressure: maxPressure,
      minPressure: minPressure,
      pressureVariance: pressureVariance
    };
  };

  const analytics = getAnalytics();

  // Prepare data for pie chart (pressure distribution)
  const pressureDistribution = React.useMemo(() => {
    if (!simulationData?.nodes) return [];

    const ranges = [
      { name: 'High (>40 PSI)', value: 0, color: '#10b981' },
      { name: 'Good (20-40 PSI)', value: 0, color: '#f59e0b' },
      { name: 'Low (10-20 PSI)', value: 0, color: '#f97316' },
      { name: 'Critical (<10 PSI)', value: 0, color: '#ef4444' }
    ];

    Object.values(simulationData.nodes).forEach(node => {
      const pressure = node.pressure || 0;
      if (pressure > 40) ranges[0].value++;
      else if (pressure > 20) ranges[1].value++;
      else if (pressure > 10) ranges[2].value++;
      else if (pressure > 0) ranges[3].value++;
    });

    return ranges.filter(range => range.value > 0);
  }, [simulationData]);

  const handleExport = () => {
    // Simple CSV export
    const csvData = chartData.map(d => ({
      time: d.time,
      demand: d.demand,
      pressure: d.pressure,
      flow: d.flow
    }));
    
    const csv = [
      'Time,Demand (GPM),Pressure (PSI),Flow (GPM)',
      ...csvData.map(d => `${d.time},${d.demand.toFixed(2)},${d.pressure.toFixed(2)},${d.flow.toFixed(2)}`)
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'hydrotwin-analytics.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <AnalyticsContainer>
      <AnalyticsHeader>
        <Title>System Analytics</Title>
        <ExportButton onClick={handleExport}>
          <FiDownload size={16} />
          Export Data
        </ExportButton>
      </AnalyticsHeader>

      <StatsGrid>
        <StatCard>
          <StatTitle>Total Nodes</StatTitle>
          <StatValue>{analytics.totalNodes}</StatValue>
          <StatChange positive={analytics.totalNodes > 0}>
            {analytics.totalNodes > 0 ? 'Active' : 'No Data'}
          </StatChange>
        </StatCard>

        <StatCard>
          <StatTitle>Average Pressure</StatTitle>
          <StatValue>{analytics.averagePressure.toFixed(1)} PSI</StatValue>
          <StatChange positive={analytics.averagePressure > 20}>
            {analytics.averagePressure > 20 ? 'Good' : 'Low'}
          </StatChange>
        </StatCard>

        <StatCard>
          <StatTitle>Pressure Range</StatTitle>
          <StatValue>{analytics.minPressure.toFixed(1)} - {analytics.maxPressure.toFixed(1)} PSI</StatValue>
          <StatChange positive={analytics.maxPressure - analytics.minPressure < 20}>
            {analytics.maxPressure - analytics.minPressure < 20 ? 'Stable' : 'Variable'}
          </StatChange>
        </StatCard>

        <StatCard>
          <StatTitle>Pressure Variance</StatTitle>
          <StatValue>{analytics.pressureVariance.toFixed(1)}</StatValue>
          <StatChange positive={analytics.pressureVariance < 10}>
            {analytics.pressureVariance < 10 ? 'Low' : 'High'}
          </StatChange>
        </StatCard>
      </StatsGrid>

      <ChartsGrid>
        <ChartCard>
          <ChartTitle>
            <FiTrendingUp size={20} />
            Historical Trends
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="demand" stroke="#3b82f6" strokeWidth={2} name="Demand (GPM)" />
                <Line type="monotone" dataKey="pressure" stroke="#10b981" strokeWidth={2} name="Pressure (PSI)" />
                <Line type="monotone" dataKey="flow" stroke="#8b5cf6" strokeWidth={2} name="Flow (GPM)" />
              </LineChart>
            </ResponsiveContainer>
          </ChartContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>
            <FiPieChart size={20} />
            Pressure Distribution
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pressureDistribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {pressureDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </ChartContainer>
        </ChartCard>
      </ChartsGrid>

      <ChartsGrid>
        <ChartCard>
          <ChartTitle>
            <FiBarChart2 size={20} />
            Node Performance
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData.slice(-12)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="demand" fill="#3b82f6" name="Demand (GPM)" />
                <Bar dataKey="pressure" fill="#10b981" name="Pressure (PSI)" />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>
            <FiTrendingUp size={20} />
            System Efficiency
          </ChartTitle>
          <ChartContainer>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              height: '100%',
              flexDirection: 'column',
              gap: '1rem'
            }}>
              <div style={{ fontSize: '2rem', fontWeight: '700', color: '#10b981' }}>
                {((analytics.averagePressure / 50) * 100).toFixed(1)}%
              </div>
              <div style={{ fontSize: '1rem', color: '#64748b', textAlign: 'center' }}>
                System Efficiency
                <br />
                <small>Based on pressure performance</small>
              </div>
            </div>
          </ChartContainer>
        </ChartCard>
      </ChartsGrid>
    </AnalyticsContainer>
  );
};

export default Analytics;

