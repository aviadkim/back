// This is a placeholder file for UserContext.jsx
// Please paste the complete code from below in this file

/*
UserContext Component Guide:

This context provides user authentication and profile data to the entire application.
It handles:

1. User authentication state (logged in/out)
2. User profile information
3. Authentication operations (login, logout, register)
4. Loading user data from local storage or token
5. Managing user preferences

The context uses React's Context API to make user data and authentication
functions available throughout the application without prop drilling.

How to use:
- Wrap your application with the UserContextProvider
- Access user data and functions using the useUser hook
- Check authentication status with isAuthenticated
- Access current user data with userData
*/
import React, { createContext, useState, useContext, useEffect } from 'react';

// Create the context
export const UserContext = createContext(null);

/**
 * UserContextProvider component provides user authentication and profile data
 * to the entire application
 * 
 * Features:
 * - User authentication state (logged in/out)
 * - User profile information
 * - Authentication operations (login, logout, register)
 * - Loading user data from local storage or token
 * - Managing user preferences
 */
export function UserContextProvider({ children }) {
  // State for user data and authentication
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Load user from local storage or token on component mount
  useEffect(() => {
    const loadUser = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // Check if there's a token in localStorage
        const token = localStorage.getItem('authToken');
        
        if (!token) {
          setIsAuthenticated(false);
          setUser(null);
          return;
        }
        
        // Fetch user data using the token
        // This would be an API call in a real application
        // For now, we'll simulate it with a timeout
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock user data
        const userData = {
          id: '1',
          firstName: 'ישראל',
          lastName: 'ישראלי',
          email: 'user@example.com',
          role: 'user',
          preferences: {
            language: 'he',
            theme: 'light'
          }
        };
        
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error loading user:', error);
        setError('Failed to authenticate user');
        setIsAuthenticated(false);
        setUser(null);
        
        // Clean up localStorage on authentication error
        localStorage.removeItem('authToken');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadUser();
  }, []);
  
  // Login function
  const login = async (email, password) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // This would be an API call in a real application
      // For now, we'll simulate it with a timeout
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock successful login
      const mockResponse = {
        success: true,
        token: 'mock_jwt_token_123456',
        user: {
          id: '1',
          firstName: 'ישראל',
          lastName: 'ישראלי',
          email: email,
          role: 'user',
          preferences: {
            language: 'he',
            theme: 'light'
          }
        }
      };
      
      // Save token to localStorage
      localStorage.setItem('authToken', mockResponse.token);
      
      // Update state
      setUser(mockResponse.user);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      setError(error.message || 'Failed to login');
      return { success: false, error: error.message || 'Failed to login' };
    } finally {
      setIsLoading(false);
    }
  };
  
  // Logout function
  const logout = () => {
    // Clear token from localStorage
    localStorage.removeItem('authToken');
    
    // Update state
    setUser(null);
    setIsAuthenticated(false);
  };
  
  // Register function
  const register = async (firstName, lastName, email, password) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // This would be an API call in a real application
      // For now, we'll simulate it with a timeout
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock successful registration
      const mockResponse = {
        success: true,
        message: 'User registered successfully'
      };
      
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      setError(error.message || 'Failed to register');
      return { success: false, error: error.message || 'Failed to register' };
    } finally {
      setIsLoading(false);
    }
  };
  
  // Update user profile
  const updateProfile = async (profileData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // This would be an API call in a real application
      // For now, we'll simulate it with a timeout
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update user state with new profile data
      setUser(prev => ({ ...prev, ...profileData }));
      
      return { success: true };
    } catch (error) {
      console.error('Profile update error:', error);
      setError(error.message || 'Failed to update profile');
      return { success: false, error: error.message || 'Failed to update profile' };
    } finally {
      setIsLoading(false);
    }
  };
  
  // Update user preferences
  const updatePreferences = async (preferences) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // This would be an API call in a real application
      // For now, we'll simulate it with a timeout
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update user state with new preferences
      setUser(prev => ({
        ...prev,
        preferences: { ...prev.preferences, ...preferences }
      }));
      
      return { success: true };
    } catch (error) {
      console.error('Preferences update error:', error);
      setError(error.message || 'Failed to update preferences');
      return { success: false, error: error.message || 'Failed to update preferences' };
    } finally {
      setIsLoading(false);
    }
  };
  
  // Value object to be provided by the context
  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    register,
    updateProfile,
    updatePreferences
  };
  
  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}

// Custom hook for using the user context
export function useUser() {
  const context = useContext(UserContext);
  
  if (!context) {
    throw new Error('useUser must be used within a UserContextProvider');
  }
  
  return context;
}

export default UserContextProvider;
