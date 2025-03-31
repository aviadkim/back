import React, { useState } from 'react';
import {
  AppBar, Toolbar, Typography, Container, Box,
  Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, // Use ListItemButton for better semantics
  CssBaseline, IconButton, useTheme, useMediaQuery, Divider
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  UploadFile as UploadIcon,
  Article as DocumentIcon,
  Settings as SettingsIcon,
  Home as HomeIcon, // Added HomeIcon
  Analytics as AnalyticsIcon // Added AnalyticsIcon
} from '@mui/icons-material';
import { Link as RouterLink, useLocation } from 'react-router-dom'; // Import useLocation

const drawerWidth = 240;

const Layout = ({ children, title = "Financial Document Analyzer" }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation(); // Get current location

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    // { text: 'Home', icon: <HomeIcon />, path: '/' }, // Can add a separate home/landing page if needed
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' }, // Make Dashboard the root path
    { text: 'Upload Document', icon: <UploadIcon />, path: '/upload' },
    { text: 'My Documents', icon: <DocumentIcon />, path: '/documents' },
    { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' }, // Added Analytics
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' }
  ];

  const drawerContent = (
    <div>
      <Toolbar /> {/* Necessary spacer */}
      <Box sx={{ overflow: 'auto', mt: 1 }}> {/* Reduced top margin */}
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                component={RouterLink}
                to={item.path}
                selected={location.pathname === item.path} // Highlight active link
                onClick={isMobile ? handleDrawerToggle : undefined}
                sx={{
                  py: 1.2, // Adjusted padding
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25, 118, 210, 0.12)', // Custom selected background
                    '& .MuiListItemIcon-root, & .MuiListItemText-primary': {
                      color: 'primary.main', // Highlight icon and text
                    },
                  },
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.04)' // Subtle hover
                  }
                }}
              >
                <ListItemIcon sx={{ color: location.pathname === item.path ? 'primary.main' : 'inherit', minWidth: 40 }}> {/* Ensure icon color matches selection */}
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />

      {/* Top Bar */}
      <AppBar
        position="fixed"
        sx={{
          // Make AppBar full width if drawer is temporary (mobile), otherwise shift it
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          background: 'linear-gradient(135deg, #1976d2 0%, #0d47a1 100%)' // Example gradient
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }} // Only show menu button on mobile
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>
          {/* Add any AppBar actions here (e.g., user profile) */}
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        aria-label="mailbox folders"
      >
        {/* Temporary Drawer for Mobile */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawerContent}
        </Drawer>
        {/* Permanent Drawer for Desktop */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` }, // Adjust width based on drawer
          backgroundColor: (theme) => theme.palette.grey[100], // Light background for content area
          minHeight: '100vh' // Ensure content area fills height
        }}
      >
        <Toolbar /> {/* Offset for fixed AppBar */}
        <Container maxWidth="xl"> {/* Use xl for wider content area */}
          {children}
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;