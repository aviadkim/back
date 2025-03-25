import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  Breadcrumbs as MuiBreadcrumbs,
  Link,
  Typography,
  Box
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import DescriptionIcon from '@mui/icons-material/Description';
import ChatIcon from '@mui/icons-material/Chat';
import TableChartIcon from '@mui/icons-material/TableChart';
import UploadFileIcon from '@mui/icons-material/UploadFile';

/**
 * Breadcrumbs component that shows the current navigation path
 * 
 * Features:
 * - Automatically generates breadcrumbs based on the current route
 * - Provides proper icons for each route segment
 * - Supports both Hebrew and English languages
 */
function Breadcrumbs({ language = 'he' }) {
  const location = useLocation();
  
  // Generate breadcrumb items based on the current path
  const pathSegments = location.pathname.split('/').filter(Boolean);
  
  // Path mappings for translation and icons
  const pathMappings = {
    documents: {
      label: language === 'he' ? 'מסמכים' : 'Documents',
      icon: <DescriptionIcon fontSize="small" sx={{ mr: 0.5 }} />
    },
    upload: {
      label: language === 'he' ? 'העלאת מסמך' : 'Upload Document',
      icon: <UploadFileIcon fontSize="small" sx={{ mr: 0.5 }} />
    },
    chat: {
      label: language === 'he' ? 'צ\'אט' : 'Chat',
      icon: <ChatIcon fontSize="small" sx={{ mr: 0.5 }} />
    },
    tables: {
      label: language === 'he' ? 'טבלאות' : 'Tables',
      icon: <TableChartIcon fontSize="small" sx={{ mr: 0.5 }} />
    },
    new: {
      label: language === 'he' ? 'חדש' : 'New',
      icon: null
    }
  };
  
  // Don't show breadcrumbs on the home page
  if (pathSegments.length === 0) {
    return null;
  }
  
  return (
    <Box sx={{ my: 2 }}>
      <MuiBreadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        aria-label="breadcrumb"
      >
        {/* Home link always present */}
        <Link
          underline="hover"
          color="inherit"
          component={RouterLink}
          to="/"
          sx={{ display: 'flex', alignItems: 'center' }}
        >
          <HomeIcon fontSize="small" sx={{ mr: 0.5 }} />
          {language === 'he' ? 'דף הבית' : 'Home'}
        </Link>
        
        {/* Path segments */}
        {pathSegments.map((segment, index) => {
          const isLast = index === pathSegments.length - 1;
          const path = `/${pathSegments.slice(0, index + 1).join('/')}`;
          const mapping = pathMappings[segment] || {
            label: segment.charAt(0).toUpperCase() + segment.slice(1),
            icon: null
          };
          
          return isLast ? (
            <Typography
              key={path}
              color="text.primary"
              sx={{ display: 'flex', alignItems: 'center' }}
            >
              {mapping.icon}
              {mapping.label}
            </Typography>
          ) : (
            <Link
              key={path}
              underline="hover"
              color="inherit"
              component={RouterLink}
              to={path}
              sx={{ display: 'flex', alignItems: 'center' }}
            >
              {mapping.icon}
              {mapping.label}
            </Link>
          );
        })}
      </MuiBreadcrumbs>
    </Box>
  );
}

export default Breadcrumbs;
