import React, { useState, useContext } from 'react';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Menu,
  MenuItem,
  Chip,
  useTheme,
  useMediaQuery,
  Avatar
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import DescriptionIcon from '@mui/icons-material/Description';
import ChatIcon from '@mui/icons-material/Chat';
import TableChartIcon from '@mui/icons-material/TableChart';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import TranslateIcon from '@mui/icons-material/Translate';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

// Import DocumentContext
import { DocumentContext } from '../contexts/DocumentContext';

/**
 * AppNavigation component provides the main navigation for the application
 * 
 * Features:
 * - Responsive mobile/desktop navigation
 * - Active document display
 * - Language switching
 * - Theme toggling
 * - User profile menu
 */
function AppNavigation({ 
  language = 'he', 
  themeMode = 'light',
  onToggleTheme,
  onToggleLanguage
}) {
  // Router hooks
  const navigate = useNavigate();
  const location = useLocation();
  
  // Theme and responsive design
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Document context
  const { activeDocuments, setActiveDocuments } = useContext(DocumentContext);
  
  // State for mobile drawer
  const [drawerOpen, setDrawerOpen] = useState(false);
  
  // State for profile menu
  const [profileMenuAnchor, setProfileMenuAnchor] = useState(null);
  
  // Navigation items
  const navItems = [
    {
      path: '/',
      label: language === 'he' ? 'לוח בקרה' : 'Dashboard',
      icon: <DashboardIcon />
    },
    {
      path: '/documents',
      label: language === 'he' ? 'מסמכים' : 'Documents',
      icon: <DescriptionIcon />
    },
    {
      path: '/chat',
      label: language === 'he' ? 'צ\'אט' : 'Chat',
      icon: <ChatIcon />
    },
    {
      path: '/tables/new',
      label: language === 'he' ? 'טבלאות' : 'Tables',
      icon: <TableChartIcon />
    }
  ];
  
  // Toggle drawer
  const toggleDrawer = (open) => (event) => {
    if (
      event.type === 'keydown' &&
      (event.key === 'Tab' || event.key === 'Shift')
    ) {
      return;
    }
    setDrawerOpen(open);
  };
  
  // Profile menu handlers
  const handleProfileMenuOpen = (event) => {
    setProfileMenuAnchor(event.currentTarget);
  };
  
  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null);
  };
  
  // Navigation
  const handleNavigate = (path) => {
    navigate(path);
    setDrawerOpen(false);
  };
  
  // Render drawer content
  const drawerContent = (
    <Box
      sx={{ width: 280 }}
      role="presentation"
      onClick={toggleDrawer(false)}
      onKeyDown={toggleDrawer(false)}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6" component="div">
          {language === 'he' ? 'מנתח מסמכים פיננסיים' : 'Financial Document Analyzer'}
        </Typography>
        <IconButton onClick={toggleDrawer(false)}>
          <ChevronRightIcon />
        </IconButton>
      </Box>
      
      <Divider />
      
      <List>
        {navItems.map((item) => (
          <ListItem 
            button 
            key={item.path} 
            onClick={() => handleNavigate(item.path)}
            selected={location.pathname === item.path}
          >
            <ListItemIcon>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItem>
        ))}
      </List>
      
      <Divider />
      
      <List>
        <ListItem button onClick={() => handleNavigate('/documents/upload')}>
          <ListItemIcon>
            <UploadFileIcon />
          </ListItemIcon>
          <ListItemText primary={language === 'he' ? 'העלאת מסמך' : 'Upload Document'} />
        </ListItem>
      </List>
      
      {activeDocuments.length > 0 && (
        <>
          <Divider />
          
          <Box sx={{ p: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              {language === 'he' ? 'מסמכים פעילים' : 'Active Documents'}
            </Typography>
            
            <List dense disablePadding>
              {activeDocuments.map((doc) => (
                <ListItem 
                  key={doc.id} 
                  dense
                  sx={{ py: 0.5 }}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <DescriptionIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText 
                    primary={doc.title || doc.id}
                    primaryTypographyProps={{ 
                      variant: 'body2',
                      noWrap: true,
                      style: { maxWidth: '180px' }
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </>
      )}
    </Box>
  );
  
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          {/* Mobile menu button */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={toggleDrawer(true)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          {/* Logo */}
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              flexGrow: 1,
              textDecoration: 'none',
              color: 'inherit',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            {language === 'he' ? 'מנתח מסמכים פיננסיים' : 'Financial Document Analyzer'}
          </Typography>
          
          {/* Desktop navigation */}
          {!isMobile && (
            <Box sx={{ display: 'flex', mr: 2 }}>
              {navItems.map((item) => (
                <Button
                  key={item.path}
                  color="inherit"
                  component={RouterLink}
                  to={item.path}
                  sx={{
                    mx: 0.5,
                    ...(location.pathname === item.path && {
                      borderBottom: '2px solid white',
                    }),
                  }}
                  startIcon={item.icon}
                >
                  {item.label}
                </Button>
              ))}
            </Box>
          )}
          
          {/* Theme toggle */}
          <IconButton color="inherit" onClick={onToggleTheme} sx={{ ml: 1 }}>
            {themeMode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
          
          {/* Language toggle */}
          <IconButton color="inherit" onClick={onToggleLanguage} sx={{ ml: 1 }}>
            <TranslateIcon />
          </IconButton>
          
          {/* Upload button */}
          {!isMobile && (
            <Button
              color="inherit"
              variant="outlined"
              component={RouterLink}
              to="/documents/upload"
              sx={{ ml: 2, borderColor: 'rgba(255,255,255,0.5)' }}
              startIcon={<UploadFileIcon />}
            >
              {language === 'he' ? 'העלאת מסמך' : 'Upload'}
            </Button>
          )}
          
          {/* User profile */}
          <IconButton
            color="inherit"
            onClick={handleProfileMenuOpen}
            sx={{ ml: 1 }}
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.dark' }}>
              <AccountCircleIcon />
            </Avatar>
          </IconButton>
          
          {/* Profile menu */}
          <Menu
            anchorEl={profileMenuAnchor}
            open={Boolean(profileMenuAnchor)}
            onClose={handleProfileMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={handleProfileMenuClose}>
              {language === 'he' ? 'פרופיל' : 'Profile'}
            </MenuItem>
            <MenuItem onClick={handleProfileMenuClose}>
              {language === 'he' ? 'הגדרות' : 'Settings'}
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleProfileMenuClose}>
              {language === 'he' ? 'התנתק' : 'Logout'}
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      
      {/* Mobile drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer(false)}
      >
        {drawerContent}
      </Drawer>
    </>
  );
}

export default AppNavigation;
