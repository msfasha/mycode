import React, { useState } from 'react';
import styled from 'styled-components';
import { FiSettings, FiSave, FiRefreshCw, FiWifi, FiDatabase, FiClock } from 'react-icons/fi';

const SettingsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.lg};
  height: 100%;
  max-width: 800px;
`;

const SettingsHeader = styled.div`
  margin-bottom: ${props => props.theme.spacing.md};
`;

const Title = styled.h2`
  font-size: 1.875rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const SettingsGrid = styled.div`
  display: grid;
  gap: ${props => props.theme.spacing.lg};
`;

const SettingsSection = styled.div`
  background-color: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.lg};
  box-shadow: ${props => props.theme.shadows.sm};
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const SectionTitle = styled.h3`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const SectionIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.primary + '20'};
  color: ${props => props.theme.colors.primary};
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Label = styled.label`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.text};
`;

const Input = styled.input`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const Select = styled.select`
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

const TextArea = styled.textarea`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  font-size: 0.875rem;
  min-height: 100px;
  resize: vertical;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const Checkbox = styled.input`
  width: 16px;
  height: 16px;
  cursor: pointer;
`;

const CheckboxLabel = styled.label`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.text};
  cursor: pointer;
`;

const ButtonGroup = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.lg};
  padding-top: ${props => props.theme.spacing.lg};
  border-top: 1px solid ${props => props.theme.colors.border};
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.lg};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.primary 
    ? props.theme.colors.primary 
    : props.theme.colors.surface
  };
  color: ${props => props.primary ? 'white' : props.theme.colors.text};
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;

  &:hover {
    background-color: ${props => props.primary 
      ? props.theme.colors.primary + '90' 
      : props.theme.colors.background
    };
    border-color: ${props => props.theme.colors.primary};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.status === 'connected' 
    ? props.theme.colors.success + '20' 
    : props.theme.colors.error + '20'
  };
  color: ${props => props.status === 'connected' 
    ? props.theme.colors.success 
    : props.theme.colors.error
  };
  font-size: 0.875rem;
  font-weight: 500;
`;

const Settings = () => {
  const [settings, setSettings] = useState({
    // Connection settings
    serverUrl: 'http://localhost:3001',
    websocketUrl: 'ws://localhost:3002',
    updateInterval: 30,
    
    // Simulation settings
    modelPath: './models/network.inp',
    autoRun: true,
    maxIterations: 100,
    
    // Display settings
    theme: 'light',
    language: 'en',
    timezone: 'UTC',
    
    // Alert settings
    enableAlerts: true,
    alertThreshold: 20,
    emailNotifications: false,
    emailAddress: '',
    
    // Data settings
    dataRetention: 30,
    exportFormat: 'csv',
    autoExport: false
  });

  const [isSaving, setIsSaving] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('connected');

  const handleInputChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate save delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
    console.log('Settings saved:', settings);
  };

  const handleReset = () => {
    setSettings({
      serverUrl: 'http://localhost:3001',
      websocketUrl: 'ws://localhost:3002',
      updateInterval: 30,
      modelPath: './models/network.inp',
      autoRun: true,
      maxIterations: 100,
      theme: 'light',
      language: 'en',
      timezone: 'UTC',
      enableAlerts: true,
      alertThreshold: 20,
      emailNotifications: false,
      emailAddress: '',
      dataRetention: 30,
      exportFormat: 'csv',
      autoExport: false
    });
  };

  return (
    <SettingsContainer>
      <SettingsHeader>
        <Title>System Settings</Title>
      </SettingsHeader>

      <SettingsGrid>
        <SettingsSection>
          <SectionHeader>
            <SectionIcon>
              <FiWifi size={20} />
            </SectionIcon>
            <SectionTitle>Connection Settings</SectionTitle>
          </SectionHeader>

          <FormGroup>
            <Label>Server URL</Label>
            <Input
              type="text"
              value={settings.serverUrl}
              onChange={(e) => handleInputChange('serverUrl', e.target.value)}
              placeholder="http://localhost:3001"
            />
          </FormGroup>

          <FormGroup>
            <Label>WebSocket URL</Label>
            <Input
              type="text"
              value={settings.websocketUrl}
              onChange={(e) => handleInputChange('websocketUrl', e.target.value)}
              placeholder="ws://localhost:3002"
            />
          </FormGroup>

          <FormGroup>
            <Label>Update Interval (seconds)</Label>
            <Input
              type="number"
              value={settings.updateInterval}
              onChange={(e) => handleInputChange('updateInterval', parseInt(e.target.value))}
              min="5"
              max="300"
            />
          </FormGroup>

          <StatusIndicator status={connectionStatus}>
            <FiWifi size={16} />
            {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
          </StatusIndicator>
        </SettingsSection>

        <SettingsSection>
          <SectionHeader>
            <SectionIcon>
              <FiSettings size={20} />
            </SectionIcon>
            <SectionTitle>Simulation Settings</SectionTitle>
          </SectionHeader>

          <FormGroup>
            <Label>Model File Path</Label>
            <Input
              type="text"
              value={settings.modelPath}
              onChange={(e) => handleInputChange('modelPath', e.target.value)}
              placeholder="./models/network.inp"
            />
          </FormGroup>

          <FormGroup>
            <CheckboxGroup>
              <Checkbox
                type="checkbox"
                checked={settings.autoRun}
                onChange={(e) => handleInputChange('autoRun', e.target.checked)}
              />
              <CheckboxLabel>Auto-run simulation</CheckboxLabel>
            </CheckboxGroup>
          </FormGroup>

          <FormGroup>
            <Label>Maximum Iterations</Label>
            <Input
              type="number"
              value={settings.maxIterations}
              onChange={(e) => handleInputChange('maxIterations', parseInt(e.target.value))}
              min="10"
              max="1000"
            />
          </FormGroup>
        </SettingsSection>

        <SettingsSection>
          <SectionHeader>
            <SectionIcon>
              <FiDatabase size={20} />
            </SectionIcon>
            <SectionTitle>Data Settings</SectionTitle>
          </SectionHeader>

          <FormGroup>
            <Label>Data Retention (days)</Label>
            <Input
              type="number"
              value={settings.dataRetention}
              onChange={(e) => handleInputChange('dataRetention', parseInt(e.target.value))}
              min="1"
              max="365"
            />
          </FormGroup>

          <FormGroup>
            <Label>Export Format</Label>
            <Select
              value={settings.exportFormat}
              onChange={(e) => handleInputChange('exportFormat', e.target.value)}
            >
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
              <option value="xlsx">Excel</option>
            </Select>
          </FormGroup>

          <FormGroup>
            <CheckboxGroup>
              <Checkbox
                type="checkbox"
                checked={settings.autoExport}
                onChange={(e) => handleInputChange('autoExport', e.target.checked)}
              />
              <CheckboxLabel>Enable automatic data export</CheckboxLabel>
            </CheckboxGroup>
          </FormGroup>
        </SettingsSection>

        <SettingsSection>
          <SectionHeader>
            <SectionIcon>
              <FiClock size={20} />
            </SectionIcon>
            <SectionTitle>Alert Settings</SectionTitle>
          </SectionHeader>

          <FormGroup>
            <CheckboxGroup>
              <Checkbox
                type="checkbox"
                checked={settings.enableAlerts}
                onChange={(e) => handleInputChange('enableAlerts', e.target.checked)}
              />
              <CheckboxLabel>Enable system alerts</CheckboxLabel>
            </CheckboxGroup>
          </FormGroup>

          <FormGroup>
            <Label>Alert Threshold (PSI)</Label>
            <Input
              type="number"
              value={settings.alertThreshold}
              onChange={(e) => handleInputChange('alertThreshold', parseInt(e.target.value))}
              min="0"
              max="100"
            />
          </FormGroup>

          <FormGroup>
            <CheckboxGroup>
              <Checkbox
                type="checkbox"
                checked={settings.emailNotifications}
                onChange={(e) => handleInputChange('emailNotifications', e.target.checked)}
              />
              <CheckboxLabel>Email notifications</CheckboxLabel>
            </CheckboxGroup>
          </FormGroup>

          {settings.emailNotifications && (
            <FormGroup>
              <Label>Email Address</Label>
              <Input
                type="email"
                value={settings.emailAddress}
                onChange={(e) => handleInputChange('emailAddress', e.target.value)}
                placeholder="admin@example.com"
              />
            </FormGroup>
          )}
        </SettingsSection>
      </SettingsGrid>

      <ButtonGroup>
        <Button onClick={handleSave} disabled={isSaving} primary>
          <FiSave size={16} />
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
        <Button onClick={handleReset}>
          <FiRefreshCw size={16} />
          Reset to Defaults
        </Button>
      </ButtonGroup>
    </SettingsContainer>
  );
};

export default Settings;



