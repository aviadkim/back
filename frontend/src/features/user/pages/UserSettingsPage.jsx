// This is a placeholder file for UserSettingsPage.jsx
// Please paste the complete code from below in this file

/*
UserSettingsPage Component Guide:

This component provides an interface for users to manage their account settings 
and preferences, including:

1. Profile information (name, email, etc.)
2. Application preferences (language, theme)
3. Notification settings
4. API key management (if applicable)
5. Account security options

The component handles:
- Loading user settings from the backend
- Validating user inputs
- Saving updates to the backend
- Providing feedback on save operations

How to use:
- This component should be rendered at a route like: /settings or /user/settings
- It requires authentication to access
- Changes are only saved when the user clicks the save button
*/
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Snackbar,
  IconButton,
  Tabs,
  Tab
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import CloseIcon from '@mui/icons-material/Close';
import PersonIcon from '@mui/icons-material/Person';
import NotificationsIcon from '@mui/icons-material/Notifications';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import LanguageIcon from '@mui/icons-material/Language';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import SecurityIcon from '@mui/icons-material/Security';

/**
 * UserSettingsPage allows users to manage their profile and application preferences
 * 
 * Features:
 * - Profile information management (name, email, etc.)
 * - Application preferences (language, theme)
 * - Notification settings
 * - API key management (if applicable)
 * - Account security options
 */
function UserSettingsPage({ language = 'he' }) {
  // Tab state
  const [activeTab, setActiveTab] = useState(0);
  
  // User profile state
  const [profile, setProfile] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: ''
  });
  
  // Preferences state
  const [preferences, setPreferences] = useState({
    language: language,
    theme: 'light',
    dateFormat: 'DD/MM/YYYY',
    defaultCurrency: 'ILS'
  });
  
  // Notification settings
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    documentProcessingAlerts: true,
    weeklyReports: false,
    marketUpdates: false
  });
  
  // API keys state
  const [apiKeys, setApiKeys] = useState([]);
  const [showApiKey, setShowApiKey] = useState(false);
  
  // Loading and success states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Load user data on component mount
  useEffect(() => {
    loadUserData();
  }, []);
  
  // Load user data from backend
  const loadUserData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API call - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Sample data - replace with actual API response
      setProfile({
        firstName: 'ישראל',
        lastName: 'ישראלי',
        email: 'user@example.com',
        phone: '050-1234567'
      });
      
      setPreferences({
        language: language,
        theme: 'light',
        dateFormat: 'DD/MM/YYYY',
        defaultCurrency: 'ILS'
      });
      
      setNotificationSettings({
        emailNotifications: true,
        documentProcessingAlerts: true,
        weeklyReports: false,
        marketUpdates: false
      });
      
      setApiKeys([
        { id: 1, name: 'Default API Key', key: 'api_key_123456', created: '2023-01-01T00:00:00Z' }
      ]);
    } catch (error) {
      console.error('Error loading user data:', error);
      setError('Failed to load user data. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Handle profile changes
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfile(prev => ({ ...prev, [name]: value }));
  };
  
  // Handle preferences changes
  const handlePreferencesChange = (e) => {
    const { name, value } = e.target;
    setPreferences(prev => ({ ...prev, [name]: value }));
  };
  
  // Handle notification setting changes
  const handleNotificationChange = (e) => {
    const { name, checked } = e.target;
    setNotificationSettings(prev => ({ ...prev, [name]: checked }));
  };
  
  // Handle save profile
  const handleSaveProfile = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API call - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccessMessage(language === 'he' ? 'הפרופיל נשמר בהצלחה' : 'Profile saved successfully');
    } catch (error) {
      console.error('Error saving profile:', error);
      setError(language === 'he' ? 'שגיאה בשמירת הפרופיל' : 'Error saving profile');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle save preferences
  const handleSavePreferences = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API call - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccessMessage(language === 'he' ? 'ההעדפות נשמרו בהצלחה' : 'Preferences saved successfully');
    } catch (error) {
      console.error('Error saving preferences:', error);
      setError(language === 'he' ? 'שגיאה בשמירת ההעדפות' : 'Error saving preferences');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle close success message
  const handleCloseSuccess = () => {
    setSuccessMessage('');
  };
  
  // Generate new API key
  const handleGenerateApiKey = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API call - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newKey = {
        id: apiKeys.length + 1,
        name: 'New API Key',
        key: `api_key_${Math.random().toString(36).substring(2, 15)}`,
        created: new Date().toISOString()
      };
      
      setApiKeys([...apiKeys, newKey]);
      setShowApiKey(true);
      setSuccessMessage(language === 'he' ? 'מפתח API חדש נוצר בהצלחה' : 'New API key generated successfully');
    } catch (error) {
      console.error('Error generating API key:', error);
      setError(language === 'he' ? 'שגיאה ביצירת מפתח API' : 'Error generating API key');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Delete API key
  const handleDeleteApiKey = async (keyId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Simulate API call - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setApiKeys(apiKeys.filter(key => key.id !== keyId));
      setSuccessMessage(language === 'he' ? 'מפתח API נמחק בהצלחה' : 'API key deleted successfully');
    } catch (error) {
      console.error('Error deleting API key:', error);
      setError(language === 'he' ? 'שגיאה במחיקת מפתח API' : 'Error deleting API key');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      return dateString;
    }
  };
  
  if (isLoading && !profile.firstName) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" component="h1" gutterBottom>
        {language === 'he' ? 'הגדרות משתמש' : 'User Settings'}
      </Typography>
      
      {/* Settings tabs */}
      <Tabs 
        value={activeTab} 
        onChange={handleTabChange}
        sx={{ mb: 3 }}
      >
        <Tab 
          icon={<PersonIcon />} 
          label={language === 'he' ? 'פרופיל' : 'Profile'} 
          iconPosition="start"
        />
        <Tab 
          icon={<LanguageIcon />} 
          label={language === 'he' ? 'העדפות' : 'Preferences'} 
          iconPosition="start"
        />
        <Tab 
          icon={<NotificationsIcon />} 
          label={language === 'he' ? 'התראות' : 'Notifications'} 
          iconPosition="start"
        />
        <Tab 
          icon={<VpnKeyIcon />} 
          label={language === 'he' ? 'מפתחות API' : 'API Keys'} 
          iconPosition="start"
        />
        <Tab 
          icon={<SecurityIcon />} 
          label={language === 'he' ? 'אבטחה' : 'Security'} 
          iconPosition="start"
        />
      </Tabs>
      
      {/* Error alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {/* Profile tab */}
      {activeTab === 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            {language === 'he' ? 'פרטי פרופיל' : 'Profile Details'}
          </Typography>
          
          <Card variant="outlined" sx={{ p: 3, mb: 4 }}> {/* Wrap in Card */}
            <Grid container spacing={3}> {/* Removed mb from Grid */}
              <Grid item xs={12} sm={6}>
                <TextField
                fullWidth
                label={language === 'he' ? 'שם פרטי' : 'First Name'}
                name="firstName"
                value={profile.firstName}
                onChange={handleProfileChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={language === 'he' ? 'שם משפחה' : 'Last Name'}
                name="lastName"
                value={profile.lastName}
                onChange={handleProfileChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={language === 'he' ? 'כתובת אימייל' : 'Email Address'}
                name="email"
                type="email"
                value={profile.email}
                onChange={handleProfileChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={language === 'he' ? 'טלפון' : 'Phone Number'}
                name="phone"
                value={profile.phone}
                onChange={handleProfileChange}
              />
            </Grid>
          </Grid>
         </Card> {/* Close Card */}
          
          <Button
            variant="contained"
            color="primary"
            startIcon={isLoading ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSaveProfile}
            disabled={isLoading}
          >
            {language === 'he' ? 'שמור שינויים' : 'Save Changes'}
          </Button>
        </Box>
      )}
      
      {/* Preferences tab */}
      {activeTab === 1 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            {language === 'he' ? 'העדפות אפליקציה' : 'Application Preferences'}
          </Typography>
          
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="language-label">
                  {language === 'he' ? 'שפה' : 'Language'}
                </InputLabel>
                <Select
                  labelId="language-label"
                  name="language"
                  value={preferences.language}
                  label={language === 'he' ? 'שפה' : 'Language'}
                  onChange={handlePreferencesChange}
                >
                  <MenuItem value="he">עברית</MenuItem>
                  <MenuItem value="en">English</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="theme-label">
                  {language === 'he' ? 'ערכת נושא' : 'Theme'}
                </InputLabel>
                <Select
                  labelId="theme-label"
                  name="theme"
                  value={preferences.theme}
                  label={language === 'he' ? 'ערכת נושא' : 'Theme'}
                  onChange={handlePreferencesChange}
                >
                  <MenuItem value="light">{language === 'he' ? 'בהיר' : 'Light'}</MenuItem>
                  <MenuItem value="dark">{language === 'he' ? 'כהה' : 'Dark'}</MenuItem>
                  <MenuItem value="system">{language === 'he' ? 'לפי הגדרות מערכת' : 'System'}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="date-format-label">
                  {language === 'he' ? 'פורמט תאריך' : 'Date Format'}
                </InputLabel>
                <Select
                  labelId="date-format-label"
                  name="dateFormat"
                  value={preferences.dateFormat}
                  label={language === 'he' ? 'פורמט תאריך' : 'Date Format'}
                  onChange={handlePreferencesChange}
                >
                  <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                  <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                  <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel id="currency-label">
                  {language === 'he' ? 'מטבע ברירת מחדל' : 'Default Currency'}
                </InputLabel>
                <Select
                  labelId="currency-label"
                  name="defaultCurrency"
                  value={preferences.defaultCurrency}
                  label={language === 'he' ? 'מטבע ברירת מחדל' : 'Default Currency'}
                  onChange={handlePreferencesChange}
                >
                  <MenuItem value="ILS">₪ ILS</MenuItem>
                  <MenuItem value="USD">$ USD</MenuItem>
                  <MenuItem value="EUR">€ EUR</MenuItem>
                  <MenuItem value="GBP">£ GBP</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
          
          <Button
            variant="contained"
            color="primary"
            startIcon={isLoading ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSavePreferences}
            disabled={isLoading}
          >
            {language === 'he' ? 'שמור העדפות' : 'Save Preferences'}
          </Button>
        </Box>
      )}
      
      {/* Notifications tab */}
      {activeTab === 2 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            {language === 'he' ? 'הגדרות התראות' : 'Notification Settings'}
          </Typography>
          
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.emailNotifications}
                    onChange={handleNotificationChange}
                    name="emailNotifications"
                    color="primary"
                  />
                }
                label={language === 'he' ? 'קבלת התראות במייל' : 'Receive Email Notifications'}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 2 }}>
                {language === 'he' 
                  ? 'הפעל כדי לקבל התראות מערכת במייל'
                  : 'Enable to receive system notifications via email'}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle1" gutterBottom>
                {language === 'he' ? 'סוגי התראות' : 'Notification Types'}
              </Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.documentProcessingAlerts}
                    onChange={handleNotificationChange}
                    name="documentProcessingAlerts"
                    color="primary"
                    disabled={!notificationSettings.emailNotifications}
                  />
                }
                label={language === 'he' ? 'התראות על עיבוד מסמכים' : 'Document Processing Alerts'}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.weeklyReports}
                    onChange={handleNotificationChange}
                    name="weeklyReports"
                    color="primary"
                    disabled={!notificationSettings.emailNotifications}
                  />
                }
                label={language === 'he' ? 'דוחות שבועיים' : 'Weekly Reports'}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.marketUpdates}
                    onChange={handleNotificationChange}
                    name="marketUpdates"
                    color="primary"
                    disabled={!notificationSettings.emailNotifications}
                  />
                }
                label={language === 'he' ? 'עדכוני שוק' : 'Market Updates'}
              />
            </CardContent>
          </Card>
          
          <Button
            variant="contained"
            color="primary"
            startIcon={isLoading ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSavePreferences}
            disabled={isLoading}
          >
            {language === 'he' ? 'שמור הגדרות' : 'Save Settings'}
          </Button>
        </Box>
      )}
      
      {/* API Keys tab */}
      {activeTab === 3 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            {language === 'he' ? 'מפתחות API' : 'API Keys'}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {language === 'he'
              ? 'מפתחות API מאפשרים גישה תכנותית למערכת. שמור על סודיות המפתחות שלך.'
              : 'API keys allow programmatic access to the system. Keep your keys secret.'}
          </Typography>
          
          {apiKeys.length > 0 ? (
            <Card variant="outlined" sx={{ mb: 3 }}>
              <Box
                component="table"
                sx={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  '& th, & td': {
                    px: 2,
                    py: 1.5,
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                  },
                }}
              >
                <Box component="thead" sx={{ backgroundColor: 'background.default' }}>
                  <Box component="tr">
                    <Box component="th" sx={{ textAlign: 'left' }}>
                      {language === 'he' ? 'שם' : 'Name'}
                    </Box>
                    <Box component="th" sx={{ textAlign: 'left' }}>
                      {language === 'he' ? 'מפתח' : 'Key'}
                    </Box>
                    <Box component="th" sx={{ textAlign: 'left' }}>
                      {language === 'he' ? 'נוצר' : 'Created'}
                    </Box>
                    <Box component="th" sx={{ textAlign: 'right' }}>
                      {language === 'he' ? 'פעולות' : 'Actions'}
                    </Box>
                  </Box>
                </Box>
                <Box component="tbody">
                  {apiKeys.map((apiKey) => (
                    <Box component="tr" key={apiKey.id}>
                      <Box component="td">
                        {apiKey.name}
                      </Box>
                      <Box component="td">
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2">
                            {showApiKey ? apiKey.key : '••••••••••••••••••••'}
                          </Typography>
                          <IconButton 
                            size="small" 
                            onClick={() => setShowApiKey(!showApiKey)}
                            sx={{ ml: 1 }}
                          >
                            {showApiKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                          </IconButton>
                        </Box>
                      </Box>
                      <Box component="td">
                        {formatDate(apiKey.created)}
                      </Box>
                      <Box component="td" sx={{ textAlign: 'right' }}>
                        <Button
                          variant="outlined"
                          size="small"
                          color="error"
                          onClick={() => handleDeleteApiKey(apiKey.id)}
                        >
                          {language === 'he' ? 'מחק' : 'Delete'}
                        </Button>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </Box>
            </Card>
          ) : (
            <Alert severity="info" sx={{ mb: 3 }}>
              {language === 'he'
                ? 'אין לך מפתחות API. צור מפתח חדש להתחלה.'
                : 'You don\'t have any API keys. Generate a new key to get started.'}
            </Alert>
          )}
          
          <Button
            variant="contained"
            color="primary"
            onClick={handleGenerateApiKey}
            disabled={isLoading}
          >
            {language === 'he' ? 'צור מפתח API חדש' : 'Generate New API Key'}
          </Button>
        </Box>
      )}
      
      {/* Security tab */}
      {activeTab === 4 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            {language === 'he' ? 'הגדרות אבטחה' : 'Security Settings'}
          </Typography>
          
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                {language === 'he' ? 'שינוי סיסמה' : 'Change Password'}
              </Typography>
              
              <Grid container spacing={3} sx={{ mb: 2 }}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    type="password"
                    label={language === 'he' ? 'סיסמה נוכחית' : 'Current Password'}
                    name="currentPassword"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="password"
                    label={language === 'he' ? 'סיסמה חדשה' : 'New Password'}
                    name="newPassword"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="password"
                    label={language === 'he' ? 'אימות סיסמה חדשה' : 'Confirm New Password'}
                    name="confirmPassword"
                  />
                </Grid>
              </Grid>
              
              <Button
                variant="contained"
                color="primary"
                disabled={isLoading}
              >
                {language === 'he' ? 'עדכון סיסמה' : 'Update Password'}
              </Button>
              
              <Divider sx={{ my: 3 }} />
              
              <Typography variant="subtitle1" gutterBottom>
                {language === 'he' ? 'אבטחה נוספת' : 'Additional Security'}
              </Typography>
              
              <FormControlLabel
                control={<Switch color="primary" />}
                label={language === 'he' ? 'אימות דו-שלבי' : 'Two-Factor Authentication'}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {language === 'he'
                  ? 'הוסף שכבת אבטחה נוספת באמצעות קוד חד-פעמי בנוסף לסיסמה'
                  : 'Add an additional layer of security using a one-time code in addition to your password'}
              </Typography>
              
              <FormControlLabel
                control={<Switch color="primary" />}
                label={language === 'he' ? 'התראות כניסה חריגה' : 'Login Alerts'}
              />
              <Typography variant="body2" color="text.secondary">
                {language === 'he'
                  ? 'קבל התראות כאשר מזוהה כניסה ממיקום או מכשיר חדש'
                  : 'Receive alerts when a login is detected from a new location or device'}
              </Typography>
            </CardContent>
          </Card>
          
          <Button
            variant="contained"
            color="primary"
            startIcon={isLoading ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSavePreferences}
            disabled={isLoading}
          >
            {language === 'he' ? 'שמור הגדרות' : 'Save Settings'}
          </Button>
        </Box>
      )}
      
      {/* Success message */}
      <Snackbar
        open={Boolean(successMessage)}
        autoHideDuration={6000}
        onClose={handleCloseSuccess}
        message={successMessage}
        action={
          <IconButton
            size="small"
            color="inherit"
            onClick={handleCloseSuccess}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        }
      />
    </Paper>
  );
}

export default UserSettingsPage;
