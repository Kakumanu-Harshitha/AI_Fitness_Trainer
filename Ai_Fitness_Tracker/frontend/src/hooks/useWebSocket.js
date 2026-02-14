import { useState, useEffect, useRef, useCallback } from 'react';
import { WS_URL } from '../utils/api';
import { useApp } from '../contexts/AppContext';

const WS_RECONNECT_DELAY = 1000;
const WS_MAX_RECONNECT_ATTEMPTS = 5;

export const useWebSocket = (path = '/ws') => {
  const { token, user } = useApp();
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const ws = useRef(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimer = useRef(null);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    try {
      const identifier = token || user?.username || 'anonymous';
      const socketUrl = `${WS_URL}${path}?token=${identifier}`;
      
      ws.current = new WebSocket(socketUrl);

      ws.current.onopen = () => {
        setIsConnected(true);
        reconnectAttempts.current = 0;
        console.log('[WebSocket] Connected');
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
        } catch (e) {
          console.warn('[WebSocket] Failed to parse message:', event.data);
          setLastMessage(event.data);
        }
      };

      ws.current.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
      };

      ws.current.onclose = (event) => {
        setIsConnected(false);
        console.log('[WebSocket] Disconnected:', event.code, event.reason);
        
        if (event.code !== 1000 && reconnectAttempts.current < WS_MAX_RECONNECT_ATTEMPTS) {
          const delay = WS_RECONNECT_DELAY * Math.pow(2, reconnectAttempts.current);
          reconnectTimer.current = setTimeout(() => {
            reconnectAttempts.current += 1;
            connect();
          }, delay);
        }
      };
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error);
    }
  }, [token, user, path]);

  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
    }
    if (ws.current) {
      ws.current.close(1000, 'Normal closure');
      ws.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      const payload = typeof message === 'string' ? message : JSON.stringify(message);
      ws.current.send(payload);
    } else {
      console.warn('[WebSocket] Cannot send message: Not connected');
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
  };
};
