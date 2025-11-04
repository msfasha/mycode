import React from 'react';
import styled from 'styled-components';
import { 
  FiMenu, 
  FiWifi, 
  FiWifiOff, 
  FiAlertCircle, 
  FiClock,
  FiActivity
} from 'react-icons/fi';

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  background-color: ${props => props.theme.colors.surface};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  box-shadow: ${props => props.theme.shadows.sm};
  z-index: 100;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const MenuButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: transparent;
  color: ${props => props.theme.colors.text};
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: ${props => props.theme.colors.background};
  }
`;

const Title = styled.h1`
  font-size: 1.5rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.lg};
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => {
    switch (props.status) {
      case 'connected':
        return props.theme.colors.success + '20';
      case 'connecting':
        return props.theme.colors.warning + '20';
      case 'disconnected':
        return props.theme.colors.error + '20';
      default:
        return props.theme.colors.secondary + '20';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'connected':
        return props.theme.colors.success;
      case 'connecting':
        return props.theme.colors.warning;
      case 'disconnected':
        return props.theme.colors.error;
      default:
        return props.theme.colors.secondary;
    }
  }};
  font-size: 0.875rem;
  font-weight: 500;
`;

const AlertBadge = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.count > 0 
    ? props.theme.colors.error + '20' 
    : props.theme.colors.background
  };
  color: ${props => props.count > 0 
    ? props.theme.colors.error 
    : props.theme.colors.textSecondary
  };
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background-color: ${props => props.count > 0 
      ? props.theme.colors.error + '30' 
      : props.theme.colors.background
    };
  }
`;

const AlertCount = styled.span`
  position: absolute;
  top: -4px;
  right: -4px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background-color: ${props => props.theme.colors.error};
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
`;

const TimeDisplay = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
`;

const Header = ({ 
  onToggleSidebar, 
  connectionStatus, 
  alertsCount = 0 
}) => {
  const [currentTime, setCurrentTime] = React.useState(new Date());

  React.useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const getConnectionIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <FiWifi />;
      case 'connecting':
        return <FiActivity />;
      case 'disconnected':
        return <FiWifiOff />;
      default:
        return <FiWifiOff />;
    }
  };

  const getConnectionText = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'disconnected':
        return 'Disconnected';
      default:
        return 'Unknown';
    }
  };

  return (
    <HeaderContainer>
      <LeftSection>
        <MenuButton onClick={onToggleSidebar}>
          <FiMenu size={20} />
        </MenuButton>
        <Title>HydroTwinJS</Title>
      </LeftSection>

      <RightSection>
        <StatusIndicator status={connectionStatus}>
          {getConnectionIcon()}
          {getConnectionText()}
        </StatusIndicator>

        <TimeDisplay>
          <FiClock size={16} />
          {currentTime.toLocaleTimeString()}
        </TimeDisplay>

        <AlertBadge count={alertsCount}>
          <FiAlertCircle size={20} />
          {alertsCount > 0 && (
            <AlertCount>
              {alertsCount > 99 ? '99+' : alertsCount}
            </AlertCount>
          )}
        </AlertBadge>
      </RightSection>
    </HeaderContainer>
  );
};

export default Header;



