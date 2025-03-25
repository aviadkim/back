// This is a placeholder file for StatisticsCard.jsx
// Please paste the complete code from below in this file

/*
StatisticsCard Component Guide:

This component displays a single statistic in a card format, with:
- An icon representing the statistic type
- A title describing what the statistic represents
- A value displaying the actual data
- Optional trend indicator (increase/decrease)

The component is designed to be used on dashboards to show key metrics like:
- Number of documents processed
- Financial totals or averages
- System activity metrics
- User engagement statistics

How to use:
- Pass the title, value, icon, and color props
- Optionally pass trend data to show change indicators
- Use multiple StatisticsCard components in a grid layout for a dashboard view
*/
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Tooltip
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

/**
 * StatisticsCard displays a single statistic in a card format
 * 
 * Features:
 * - Shows an icon representing the statistic type
 * - Displays a title describing what the statistic represents
 * - Shows the actual value of the statistic
 * - Optionally displays a trend indicator (increase/decrease)
 * - Supports a help tooltip for additional information
 */
function StatisticsCard({
  title,
  value,
  icon,
  color = 'primary',
  trendValue,
  trendDirection,
  tooltip,
  language = 'he'
}) {
  // Format trend value for display (e.g., +15.2%)
  const formatTrendValue = () => {
    if (trendValue === undefined || trendValue === null) return null;
    
    const prefix = trendDirection === 'up' ? '+' : '';
    return `${prefix}${trendValue}%`;
  };
  
  // Get trend color (green for up, red for down, or custom)
  const getTrendColor = () => {
    if (!trendDirection) return 'text.secondary';
    
    return trendDirection === 'up' ? 'success.main' : 'error.main';
  };
  
  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        borderRadius: 2,
        boxShadow: 1
      }}
    >
      <CardContent sx={{ flexGrow: 1, py: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: `${color}.light`,
              color: `${color}.main`,
              borderRadius: '50%',
              p: 1,
              width: 40,
              height: 40
            }}
          >
            {icon}
          </Box>
          
          {tooltip && (
            <Tooltip title={tooltip}>
              <IconButton size="small">
                <HelpOutlineIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        
        <Typography variant="h5" component="div" sx={{ mt: 2, fontWeight: 'medium' }}>
          {value}
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
          
          {trendValue && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                color: getTrendColor(),
                fontSize: '0.875rem'
              }}
            >
              {trendDirection === 'up' ? (
                <TrendingUpIcon fontSize="small" sx={{ mr: 0.5 }} />
              ) : (
                <TrendingDownIcon fontSize="small" sx={{ mr: 0.5 }} />
              )}
              <Typography variant="body2" component="span">
                {formatTrendValue()}
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}

export default StatisticsCard;
