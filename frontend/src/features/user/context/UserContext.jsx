import React, { createContext, useState, useCallback, useEffect } from 'react';
import axios from 'axios';

// Create the user context
export const UserContext = createContext();

/**
 * User Context Provider component
 * Manages user authentication and settings following Vertical Slice Architecture
 * 
 * Responsibilities:
 * - User authentication (login/logout)
 * - Loading user profile
 * - Updating user settings
 * - Managing user preferences
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {JSX.Element} The provider component
 */
export const UserContextProvider = ({ children }) => {
  // User state
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userSettings, setUserSettings] = useState({
    defaultLanguage: 'he',
    theme: 'light',
    notifications: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Load user profile on mount
   */
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    
    if (token) {
      loadUserProfile();
    }
  }, []);

  /**
   * Set auth token in axios headers
   * 
   * @param {string} token - Authentication token
   */
  const setAuthToken = useCallback((token) => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('authToken', token);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('authToken');
    }
  }, []);

  /**
   * Load user profile from the API
   */
  const loadUserProfile = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('/api/user/profile');
      setUser(response.data);
      setIsAuthenticated(true);
      
      // Load user settings
      const settingsResponse = await axios.get('/api/user/settings');
      setUserSettings(settingsResponse.data);
      
      return response.data;
    } catch (err) {
      console.error('Error loading user profile:', err);
      setError(err.message || 'Failed to load user profile');
      setIsAuthenticated(false);
      setAuthToken(null);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setAuthToken]);

  /**
   * Login user
   * 
   * @param {Object} credentials - User credentials
   * @param {string} credentials.email - User email
   * @param {string} credentials.password - User password
   * @returns {Object} User data
   */
  const login = useCallback(async (credentials) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('/api/auth/login', credentials);
      
      const { token, user } = response.data;
      
      setAuthToken(token);
      setUser(user);
      setIsAuthenticated(true);
      
      // Load user settings
      const settingsResponse = await axios.get('/api/user/settings');
      setUserSettings(settingsResponse.data);
      
      return user;
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [setAuthToken]);

  /**
   * Logout user
   */
  const logout = useCallback(() => {
    setAuthToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setUserSettings({
      defaultLanguage: 'he',
      theme: 'light',
      notifications: true,
    });
  }, [setAuthToken]);

  /**
   * Update user settings
   * 
   * @param {Object} settings - User settings
   * @returns {Object} Updated settings
   */
  const updateUserSettings = useCallback(async (settings) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.put('/api/user/settings', settings);
      setUserSettings(response.data);
      
      return response.data;
    } catch (err) {
      console.error('Error updating user settings:', err);
      setError(err.message || 'Failed to update user settings');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Update user profile
   * 
   * @param {Object} profileData - User profile data
   * @returns {Object} Updated user profile
   */
  const updateUserProfile = useCallback(async (profileData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.put('/api/user/profile', profileData);
      setUser(response.data);
      
      return response.data;
    } catch (err) {
      console.error('Error updating user profile:', err);
      setError(err.message || 'Failed to update user profile');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Context value
  const contextValue = {
    user,
    isAuthenticated,
    userSettings,
    loading,
    error,
    login,
    logout,
    updateUserSettings,
    updateUserProfile,
  };

  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  );
};

export default UserContext;
