import React from 'react';
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
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Mood as MoodIcon,
  Book as BookIcon,
  Chat as ChatIcon,
  Psychology as PsychologyIcon,
  LocalLibrary as ResourcesIcon,
  Person as PersonIcon,
  Favorite as HeartIcon,
} from '@mui/icons-material';

const drawerWidth = 260;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Mood Tracker', icon: <MoodIcon />, path: '/mood' },
  { text: 'Journal', icon: <BookIcon />, path: '/journal' },
  { text: 'AI Chat', icon: <ChatIcon />, path: '/chat' },
  { text: 'Multimodal Analysis', icon: <PsychologyIcon />, path: '/multimodal' },
  { text: 'Resources', icon: <ResourcesIcon />, path: '/resources' },
  { text: 'Profile', icon: <PersonIcon />, path: '/profile' },
];

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <HeartIcon sx={{ color: 'primary.main', fontSize: 32 }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
              MindCare
            </Typography>
            <Typography variant="caption" color="text.secondary">
              AI Mental Health
            </Typography>
          </Box>
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1, py: 2 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  backgroundColor: isActive ? 'primary.main' : 'transparent',
                  color: isActive ? 'white' : 'text.primary',
                  '&:hover': {
                    backgroundColor: isActive ? 'primary.dark' : 'action.hover',
                  },
                  '& .MuiListItemIcon-root': {
                    color: isActive ? 'white' : 'text.secondary',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isActive ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      <Box sx={{ flexGrow: 1 }} />
      <Box sx={{ p: 2, backgroundColor: 'primary.light', m: 2, borderRadius: 2 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'white', mb: 0.5 }}>
          Need Help?
        </Typography>
        <Typography variant="caption" sx={{ color: 'white', opacity: 0.9 }}>
          Crisis Hotline: 988
        </Typography>
      </Box>
    </Drawer>
  );
}

export default Navigation;

// Made with Bob
