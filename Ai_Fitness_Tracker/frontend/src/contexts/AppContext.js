import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { API_URL } from '../utils/api';

const AppContext = createContext(undefined);

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

const DEFAULT_SETTINGS = {
  voiceCoachEnabled: true,
  audioCuesEnabled: true,
  theme: 'default',
  notifications: true,
  aiComplexity: 'Balanced',
};

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);

  const logout = useCallback(async () => {
    localStorage.removeItem('userToken');
    localStorage.removeItem('userData');
    setToken(null);
    setUser(null);
  }, []);

  const fetchUserProfile = useCallback(async (authToken) => {
    console.log(`[AppContext] Fetching profile from: ${API_URL}/profile`);
    try {
      const response = await fetch(`${API_URL}/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        localStorage.setItem('userData', JSON.stringify(userData));
        return userData;
      } else if (response.status === 401) {
        await logout();
      } else {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to fetch profile');
      }
    } catch (error) {
      console.error('[AppContext] Profile fetch error:', error);
      throw error;
    }
  }, [logout]);

  const initializeApp = useCallback(async () => {
    try {
      setLoading(true);
      const storedToken = localStorage.getItem('userToken');
      const storedSettings = localStorage.getItem('appSettings');

      if (storedToken) {
        setToken(storedToken);
        try {
          await fetchUserProfile(storedToken);
        } catch (e) {
          const cachedUser = localStorage.getItem('userData');
          if (cachedUser) {
            setUser(JSON.parse(cachedUser));
          }
        }
      }

      if (storedSettings) {
        setSettings({ ...DEFAULT_SETTINGS, ...JSON.parse(storedSettings) });
      }
    } catch (error) {
      console.error('[AppContext] Initialization error:', error);
    } finally {
      setLoading(false);
    }
  }, [fetchUserProfile]);

  useEffect(() => {
    initializeApp();
  }, [initializeApp]);

  const login = async (username, password) => {
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        const error = await response.json();
        throw error;
      }

      const data = await response.json();
      const newToken = data.access_token;

      localStorage.setItem('userToken', newToken);
      setToken(newToken);
      await fetchUserProfile(newToken);
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.detail || error.message || 'Login failed' };
    }
  };

  const signup = async (username, password, email) => {
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, email })
      });

      if (!response.ok) {
        const error = await response.json();
        throw error;
      }

      const data = await response.json();
      const newToken = data.access_token;

      localStorage.setItem('userToken', newToken);
      setToken(newToken);
      await fetchUserProfile(newToken);
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.detail || error.message || 'Signup failed' };
    }
  };

  const updateSettings = async (newSettings) => {
    const updated = { ...settings, ...newSettings };
    setSettings(updated);
    localStorage.setItem('appSettings', JSON.stringify(updated));
  };

  const value = {
    user,
    token,
    loading,
    settings,
    isAuthenticated: !!token,
    login,
    signup,
    logout,
    updateSettings,
    refreshUserData: () => fetchUserProfile(token)
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};
