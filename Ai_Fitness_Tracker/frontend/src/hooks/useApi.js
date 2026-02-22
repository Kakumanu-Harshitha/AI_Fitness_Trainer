import { useState, useCallback } from 'react';
import { useApp } from '../contexts/AppContext';
import { API_URL, REQUEST_TIMEOUT } from '../utils/api';

export const useApi = () => {
  const { token, logout } = useApp();
  const [loading, setLoading] = useState(false);

  const request = useCallback(async (endpoint, options = {}) => {
    const { 
      timeout = REQUEST_TIMEOUT, 
      skipAuth = false, 
      headers = {}, 
      ...rest 
    } = options;

    setLoading(true);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const fullUrl = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;
    
    const isFormData = options.body instanceof FormData;

    const requestHeaders = {
      'Accept': 'application/json',
      ...headers,
    };

    if (!isFormData) {
      requestHeaders['Content-Type'] = 'application/json';
    }

    if (token && !skipAuth) {
      requestHeaders['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(fullUrl, {
        ...rest,
        headers: requestHeaders,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.status === 401 && !skipAuth) {
        await logout();
        throw new Error('Session expired. Please log in again.');
      }

      const data = await response.json();

      if (!response.ok) {
        throw data;
      }

      return data;
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timed out');
      }
      throw error;
    } finally {
      setLoading(false);
    }
  }, [token, logout]);

  const get = useCallback((endpoint, options) => 
    request(endpoint, { ...options, method: 'GET' }), [request]);

  const post = useCallback((endpoint, body, options = {}) => {
    const isFormData = body instanceof FormData;
    return request(endpoint, {
      ...options,
      method: 'POST',
      body: isFormData ? body : JSON.stringify(body),
    });
  }, [request]);

  const put = useCallback((endpoint, body, options = {}) => {
    const isFormData = body instanceof FormData;
    return request(endpoint, {
      ...options,
      method: 'PUT',
      body: isFormData ? body : JSON.stringify(body),
    });
  }, [request]);

  const del = useCallback((endpoint, options) => 
    request(endpoint, { ...options, method: 'DELETE' }), [request]);

  return { loading, get, post, put, del, request };
};
