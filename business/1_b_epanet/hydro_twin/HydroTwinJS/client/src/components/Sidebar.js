import React from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import {
  FiHome,
  FiMap,
  FiBarChart2,
  FiAlertCircle,
  FiSettings,
  FiChevronLeft,
  FiChevronRight
} from 'react-icons/fi';

const SidebarContainer = styled.aside`
  width: ${props => props.isOpen ? '280px' : '60px'};
  height: 100vh;
  background-color: ${props => props.theme.colors.surface};
  border-right: 1px solid ${props => props.theme.colors.border};
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  z-index: 200;
`;

const SidebarHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.theme.spacing.lg};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  min-height: 80px;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  opacity: ${props => props.isOpen ? 1 : 0};
  transition: opacity 0.3s ease;
`;

const LogoIcon = styled.div`
  width: 32px;
  height: 32px;
  border-radius: ${props => props.theme.borderRadius.md};
  background: linear-gradient(135deg, ${props => props.theme.colors.primary}, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
`;

const LogoText = styled.div`
  font-size: 1.25rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
`;

const ToggleButton = styled.button`
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
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
  }
`;

const Navigation = styled.nav`
  flex: 1;
  padding: ${props => props.theme.spacing.md} 0;
`;

const NavList = styled.ul`
  list-style: none;
  margin: 0;
  padding: 0;
`;

const NavItem = styled.li`
  margin: 0;
`;

const NavLinkStyled = styled(NavLink)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.textSecondary};
  text-decoration: none;
  transition: all 0.2s;
  position: relative;

  &:hover {
    background-color: ${props => props.theme.colors.background};
    color: ${props => props.theme.colors.text};
  }

  &.active {
    background-color: ${props => props.theme.colors.primary}20;
    color: ${props => props.theme.colors.primary};
    border-right: 3px solid ${props => props.theme.colors.primary};
  }

  &.active::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background-color: ${props => props.theme.colors.primary};
  }
`;

const NavIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
`;

const NavText = styled.span`
  font-size: 0.875rem;
  font-weight: 500;
  opacity: ${props => props.isOpen ? 1 : 0};
  transition: opacity 0.3s ease;
  white-space: nowrap;
`;

const SidebarFooter = styled.div`
  padding: ${props => props.theme.spacing.lg};
  border-top: 1px solid ${props => props.theme.colors.border};
`;

const FooterText = styled.div`
  font-size: 0.75rem;
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
  opacity: ${props => props.isOpen ? 1 : 0};
  transition: opacity 0.3s ease;
`;

const Sidebar = ({ isOpen }) => {
  const navItems = [
    {
      path: '/',
      icon: FiHome,
      label: 'Dashboard',
      exact: true
    },
    {
      path: '/network',
      icon: FiMap,
      label: 'Network Map',
      exact: false
    },
    {
      path: '/analytics',
      icon: FiBarChart2,
      label: 'Analytics',
      exact: false
    },
    {
      path: '/alerts',
      icon: FiAlertCircle,
      label: 'Alerts',
      exact: false
    },
    {
      path: '/settings',
      icon: FiSettings,
      label: 'Settings',
      exact: false
    }
  ];

  return (
    <SidebarContainer isOpen={isOpen}>
      <SidebarHeader>
        <Logo isOpen={isOpen}>
          <LogoIcon>HT</LogoIcon>
          <LogoText>HydroTwin</LogoText>
        </Logo>
        <ToggleButton>
          {isOpen ? <FiChevronLeft size={16} /> : <FiChevronRight size={16} />}
        </ToggleButton>
      </SidebarHeader>

      <Navigation>
        <NavList>
          {navItems.map((item) => (
            <NavItem key={item.path}>
              <NavLinkStyled
                to={item.path}
                exact={item.exact}
                isActive={(match, location) => {
                  if (item.exact) {
                    return location.pathname === item.path;
                  }
                  return location.pathname.startsWith(item.path);
                }}
              >
                <NavIcon>
                  <item.icon size={20} />
                </NavIcon>
                <NavText isOpen={isOpen}>{item.label}</NavText>
              </NavLinkStyled>
            </NavItem>
          ))}
        </NavList>
      </Navigation>

      <SidebarFooter>
        <FooterText isOpen={isOpen}>
          HydroTwinJS v1.0.0
          <br />
          Real-time EPANET Dashboard
        </FooterText>
      </SidebarFooter>
    </SidebarContainer>
  );
};

export default Sidebar;

