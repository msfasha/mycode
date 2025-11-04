import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
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

const FlowChart = ({ data }) => {
  // Process data for the chart
  const chartData = React.useMemo(() => {
    if (!data?.links) return [];

    return Object.entries(data.links)
      .filter(([_, link]) => link.flow !== undefined)
      .map(([id, link]) => ({
        name: id,
        flow: Math.round(Math.abs(link.flow) * 10) / 10,
        velocity: Math.round(link.velocity * 10) / 10,
        headloss: Math.round(link.headloss * 10) / 10
      }))
      .sort((a, b) => b.flow - a.flow);
  }, [data]);

  const CustomTooltipComponent = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <CustomTooltip>
          <TooltipLabel>{`Link: ${label}`}</TooltipLabel>
          <TooltipValue>Flow: {payload[0].value} GPM</TooltipValue>
          <TooltipValue>Velocity: {payload[1].value} ft/s</TooltipValue>
          <TooltipValue>Headloss: {payload[2].value} ft</TooltipValue>
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
          No flow data available
        </div>
      </ChartContainer>
    );
  }

  return (
    <ChartContainer>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis 
            dataKey="name" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            label={{ value: 'Flow (GPM)', angle: -90, position: 'insideLeft' }}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltipComponent />} />
          <Line 
            type="monotone" 
            dataKey="flow" 
            stroke="#10b981"
            strokeWidth={3}
            dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
            name="Flow"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

export default FlowChart;



