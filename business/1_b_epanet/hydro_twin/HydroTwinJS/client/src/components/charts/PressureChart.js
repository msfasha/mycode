import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import styled from 'styled-components';

const ChartContainer = styled.div`
  width: 100%;
  height: 300px;
`;

const CustomTooltip = styled.div`
  background-color: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  box-shadow: ${props => props.theme.shadows.md};
`;

const TooltipLabel = styled.div`
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const TooltipValue = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
`;

const PressureChart = ({ data }) => {
  // Process data for the chart
  const chartData = React.useMemo(() => {
    if (!data?.nodes) return [];

    return Object.entries(data.nodes)
      .filter(([_, node]) => node.pressure !== undefined && node.pressure > 0)
      .map(([id, node]) => ({
        name: id,
        pressure: Math.round(node.pressure * 10) / 10,
        head: Math.round(node.head * 10) / 10,
        demand: Math.round(node.demand * 10) / 10
      }))
      .sort((a, b) => b.pressure - a.pressure);
  }, [data]);

  const CustomTooltipComponent = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <CustomTooltip>
          <TooltipLabel>{`Node: ${label}`}</TooltipLabel>
          <TooltipValue>Pressure: {payload[0].value} PSI</TooltipValue>
          <TooltipValue>Head: {payload[1].value} ft</TooltipValue>
          <TooltipValue>Demand: {payload[2].value} GPM</TooltipValue>
        </CustomTooltip>
      );
    }
    return null;
  };

  if (chartData.length === 0) {
    return (
      <ChartContainer>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100%',
          color: '#64748b',
          fontSize: '0.875rem'
        }}>
          No pressure data available
        </div>
      </ChartContainer>
    );
  }

  return (
    <ChartContainer>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="name" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            label={{ value: 'Pressure (PSI)', angle: -90, position: 'insideLeft' }}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltipComponent />} />
          <Bar 
            dataKey="pressure" 
            fill="#3b82f6"
            radius={[4, 4, 0, 0]}
            name="Pressure"
          />
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

export default PressureChart;



