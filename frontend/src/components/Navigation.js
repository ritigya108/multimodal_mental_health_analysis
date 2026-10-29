import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Box,
  Divider,
  IconButton,
  Tooltip,
  Avatar,
  Menu,
  MenuItem,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Book as BookIcon,
  Chat as ChatIcon,
  Psychology as AssessIcon,
  Person as PersonIcon,
  Assessment as MetricsIcon,
  Quiz as PHQ8Icon,
  Settings as SettingsIcon,
  ChevronLeft as CollapseIcon,
  ChevronRight as ExpandIcon,
  FavoriteBorder as LogoIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';

const DRAWER_WIDTH_FULL = 240;
const DRAWER_WIDTH_MINI = 64;

const NAV_ITEMS = [
  { text: 'Overview',    icon: <DashboardIcon />, path: '/dashboard', group: 'main' },
  { text: 'Assessment',  icon: <AssessIcon />,    path: '/assess',    group: 'main' },
  { text: 'PHQ-8',       icon: <PHQ8Icon />,      path: '/phq8',      group: 'main' },
  { text: 'Journal',     icon: <BookIcon />,      path: '/journal',   group: 'tools' },
  { text: 'AI Chat',     icon: <ChatIcon />,      path: '/chat',      group: 'tools' },
  { text: 'Model Performance', icon: <MetricsIcon />, path: '/model', group: 'tools' },
  { text: 'Profile',     icon: <PersonIcon />,    path: '/profile',   group: 'account' },
  { text: 'Settings',    icon: <SettingsIcon />,  path: '/settings',  group: 'account' },
];

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [collapsed, setCollapsed] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const drawerWidth = collapsed ? DRAWER_WIDTH_MINI : DRAWER_WIDTH_FULL;
  const userName = localStorage.getItem('mindcare_user_name') || 'Clinician';

  const handleUserMenuOpen = (e) => setAnchorEl(e.currentTarget);
  const handleUserMenuClose = () => setAnchorEl(null);
  const handleSignOut = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('mindcare_consent');
    window.location.href = '/';
  };

  const renderGroup = (items, label) => (
    <>
      {!collapsed && (
        <Typography
          variant="caption"
          sx={{ px: 2, pt: 2, pb: 0.5, display: 'block',
                color: 'text.secondary', textTransform: 'uppercase', letterSpacing: '0.08em',
                fontWeight: 600, fontSize: '0.68rem' }}
        >
          {label}
        </Typography>
      )}
      {items.map((item) => {
        const isActive = location.pathname === item.path ||
                         location.pathname.startsWith(item.path + '/');
        return (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.25, px: collapsed ? 0.5 : 1 }}>
            <Tooltip title={collapsed ? item.text : ''} placement="right">
              <ListItemButton
                onClick={() => navigate(item.path)}
                aria-label={item.text}
                aria-current={isActive ? 'page' : undefined}
                sx={{
                  borderRadius: 2,
                  minHeight: 40,
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  px: collapsed ? 1 : 1.5,
                  backgroundColor: isActive ? 'primary.main' : 'transparent',
                  color: isActive ? 'white' : 'text.primary',
                  '&:hover': {
                    backgroundColor: isActive ? 'primary.dark' : 'action.hover',
                  },
                  '& .MuiListItemIcon-root': {
                    color: isActive ? 'white' : 'text.secondary',
                    minWidth: collapsed ? 0 : 36,
                  },
                }}
              >
                <ListItemIcon sx={{ justifyContent: 'center' }}>
                  {item.icon}
                </ListItemIcon>
                {!collapsed && (
                  <ListItemText
                    primary={item.text}
                    primaryTypographyProps={{ fontSize: '0.875rem', fontWeight: isActive ? 600 : 400 }}
                  />
                )}
              </ListItemButton>
            </Tooltip>
          </ListItem>
        );
      })}
    </>
  );

  const mainItems    = NAV_ITEMS.filter(i => i.group === 'main');
  const toolItems    = NAV_ITEMS.filter(i => i.group === 'tools');
  const accountItems = NAV_ITEMS.filter(i => i.group === 'account');

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'permanent'}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        transition: 'width 0.2s ease',
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: '1px solid',
          borderColor: 'divider',
          overflowX: 'hidden',
          transition: 'width 0.2s ease',
        },
      }}
    >
      {/* Top bar */}
      <Toolbar
        sx={{
          justifyContent: collapsed ? 'center' : 'space-between',
          px: collapsed ? 1 : 2,
          minHeight: '56px !important',
        }}
      >
        {!collapsed && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LogoIcon sx={{ color: 'primary.main', fontSize: 22 }} />
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'text.primary' }}>
              MindCare
            </Typography>
          </Box>
        )}
        <Tooltip title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
          <IconButton
            onClick={() => setCollapsed(!collapsed)}
            size="small"
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            sx={{ color: 'text.secondary' }}
          >
            {collapsed ? <ExpandIcon fontSize="small" /> : <CollapseIcon fontSize="small" />}
          </IconButton>
        </Tooltip>
      </Toolbar>

      <Divider />

      {/* User row */}
      <Box
        sx={{
          px: collapsed ? 1 : 2,
          py: 1.5,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          cursor: 'pointer',
        }}
        onClick={handleUserMenuOpen}
        aria-label="User menu"
      >
        <Avatar
          sx={{ width: 32, height: 32, fontSize: '0.875rem',
                bgcolor: 'primary.main', flexShrink: 0 }}
        >
          {userName.charAt(0).toUpperCase()}
        </Avatar>
        {!collapsed && (
          <>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, noWrap: true }}>
                {userName}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Screening user
              </Typography>
            </Box>
          </>
        )}
      </Box>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleUserMenuClose}
        transformOrigin={{ horizontal: 'left', vertical: 'top' }}
      >
        <MenuItem onClick={() => { handleUserMenuClose(); navigate('/profile'); }}>
          <PersonIcon fontSize="small" sx={{ mr: 1 }} /> Profile
        </MenuItem>
        <MenuItem onClick={() => { handleUserMenuClose(); navigate('/settings'); }}>
          <SettingsIcon fontSize="small" sx={{ mr: 1 }} /> Settings
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleSignOut} sx={{ color: 'error.main' }}>
          <LogoutIcon fontSize="small" sx={{ mr: 1 }} /> Sign out
        </MenuItem>
      </Menu>

      <Divider />

      {/* Navigation items */}
      <List sx={{ py: 1, flex: 1 }} role="navigation" aria-label="Main navigation">
        {renderGroup(mainItems, 'Screening')}
        {renderGroup(toolItems, 'Tools')}
        {renderGroup(accountItems, 'Account')}
      </List>
    </Drawer>
  );
}

export default Navigation;
