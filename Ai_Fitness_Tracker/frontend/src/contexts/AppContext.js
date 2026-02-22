import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { API_URL, WS_URL, API_V1_STR } from '../utils/api';

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
  theme: 'dark',
  notifications: true,
  aiComplexity: 'Balanced',
};

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  
  // Theme Management
  useEffect(() => {
    const root = window.document.documentElement;
    if (settings.theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('appSettings', JSON.stringify(settings));
  }, [settings]);
  const [duelInvite, setDuelInvite] = useState(null);
  const [duelActive, setDuelActive] = useState(false);
  const [duelData, setDuelData] = useState(null);
  const ws = useRef(null);

  const logout = useCallback(async () => {
    localStorage.removeItem('userToken');
    localStorage.removeItem('userData');
    setToken(null);
    setUser(null);
    
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  // WebSocket Connection
  useEffect(() => {
    if (token && !ws.current) {
      // Connect to /api/v1/ws
      const url = `${WS_URL}${API_V1_STR}/ws?token=${token}`;
      console.log('[AppContext] Connecting to WS:', url);
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        console.log('[AppContext] WS Connected');
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'duel_invite') {
            console.log('[AppContext] Duel Invite:', message);
            setDuelInvite(message);
          } else if (message.type === 'duel_start') {
            console.log('[AppContext] Duel Start:', message);
            setDuelActive(true);
            setDuelData({
              opponent: message.opponent,
              exercise: message.exercise
            });
            setDuelInvite(null);
          } else if (message.type === 'opponent_progress') {
            // Dispatch event for active components
            window.dispatchEvent(new CustomEvent('duel-progress', { detail: message }));
          } else if (message.type === 'chat_received') {
            console.log('[AppContext] Chat Received:', message);
            
            // Don't show notification if user is already in chat with this person
            if (window.location.pathname.includes(`/chat/${message.from}`)) {
              return;
            }

            // Trigger global notification
            window.dispatchEvent(new CustomEvent('new-notification', { 
              detail: {
                type: 'message',
                title: message.from,
                message: message.message,
                data: message
              } 
            }));
          }
        } catch (e) {
          console.error('[AppContext] WS Parse Error:', e);
        }
      };

      ws.current.onclose = () => {
        console.log('[AppContext] WS Disconnected');
        ws.current = null;
      };
    }

    return () => {
      if (!token && ws.current) {
        ws.current.close();
        ws.current = null;
      }
    };
  }, [token]);

  const sendDuelRequest = (targetId, exercise) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'duel_request',
        target_id: targetId,
        exercise
      }));
    } else {
      console.warn('[AppContext] WS not connected, cannot send duel request');
    }
  };

  const acceptDuel = (invite) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'duel_accept',
        challenger_id: invite.from,
        exercise: invite.exercise
      }));
    }
  };

  const rejectDuel = () => {
    setDuelInvite(null);
  };

  const sendDuelProgress = (reps, opponentId) => {
     if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'duel_progress',
        opponent_id: opponentId,
        reps
      }));
    }
  };

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
      const cachedUser = localStorage.getItem('userData');

      if (storedToken) {
        setToken(storedToken);
        
        // Optimistic UI: If we have cached user data, show it immediately
        if (cachedUser) {
          try {
            const parsedUser = JSON.parse(cachedUser);
            setUser(parsedUser);
            // We have data, so stop loading screen
            setLoading(false); 
          } catch (e) {
            console.error('[AppContext] Failed to parse cached user data', e);
          }
        }

        // Fetch fresh data in background (or foreground if no cache)
        try {
          // If we already set user from cache, we don't need to await this to show UI
          // But we want to ensure we handle the result
          const freshDataPromise = fetchUserProfile(storedToken);
          
          if (!cachedUser) {
            await freshDataPromise;
          }
        } catch (e) {
          console.error('[AppContext] Background profile fetch failed:', e);
          // If we didn't have cache and fetch failed, we might want to logout or show error
          // But fetchUserProfile already handles logout on 401
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
      const userData = await fetchUserProfile(newToken);
      
      return { success: true, user: userData };
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
      const userData = await fetchUserProfile(newToken);
      
      return { success: true, user: userData };
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
    setUser,
    token,
    loading,
    settings,
    isAuthenticated: !!token,
    login,
    signup,
    logout,
    updateSettings,
    refreshUserData: () => fetchUserProfile(token),
    // Duel Exports
    duelInvite,
    duelActive,
    setDuelActive, // Allow resetting
    duelData,
    sendDuelRequest,
    acceptDuel,
    rejectDuel,
    sendDuelProgress
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};
