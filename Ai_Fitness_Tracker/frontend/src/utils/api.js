/**
 * API Configuration for React Web Frontend
 */

// Dynamically determine the API URL based on the current hostname
// This allows the app to work on both localhost and network devices (mobile)
const getApiBaseUrl = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // If running in browser environment
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // If we're on localhost, use 127.0.0.1 to avoid IPv6 issues
    if (hostname === 'localhost') {
      return 'http://127.0.0.1:8000';
    }
    // Otherwise use the IP address (for mobile testing)
    return `http://${hostname}:8000`;
  }
  
  // Fallback for non-browser environments
  return 'http://127.0.0.1:8000';
};

export const API_BASE_URL = getApiBaseUrl();
export const API_V1_STR = '/api/v1';
export const API_URL = `${API_BASE_URL}${API_V1_STR}`;
export const AUTH_URL = `${API_URL}/auth`;
export const WS_URL = API_BASE_URL.replace('http', 'ws');

export const REQUEST_TIMEOUT = 15000;

export const getErrorMessage = (status, detail) => {
  if (detail) return detail;

  switch (status) {
    case 400: return 'Invalid request. Please check your data.';
    case 401: return 'Unauthorized. Please log in again.';
    case 403: return 'Access denied.';
    case 404: return 'Resource not found.';
    case 422: return 'Validation error.';
    case 429: return 'Too many requests. Please slow down.';
    case 500: return 'Internal server error. Our team is looking into it.';
    default: return 'Something went wrong. Please try again later.';
  }
};

export const forgotPassword = async (email) => {
  try {
    const response = await fetch(`${AUTH_URL}/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to send reset email');
    }
    
    return data;
  } catch (error) {
    throw error;
  }
};

export const resetPassword = async (token, newPassword) => {
  try {
    const response = await fetch(`${AUTH_URL}/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token, new_password: newPassword }),
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to reset password');
    }
    
    return data;
  } catch (error) {
    throw error;
  }
};

export const setupTOTP = async (token) => {
  try {
    const response = await fetch(`${AUTH_URL}/totp/setup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to setup TOTP');
    }
    
    return data;
  } catch (error) {
    throw error;
  }
};

export const verifyTOTP = async (token, otp) => {
  try {
    const response = await fetch(`${AUTH_URL}/totp/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ otp }),
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to verify TOTP');
    }
    
    return data;
  } catch (error) {
    throw error;
  }
};

export const changePassword = async (token, newPassword, totpCode = null) => {
  try {
    const response = await fetch(`${AUTH_URL}/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ 
        new_password: newPassword,
        totp_code: totpCode
      }),
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Failed to change password');
    }
    
    return data;
  } catch (error) {
    throw error;
  }
};

console.log('[API] Configuration initialized:', {
  API_BASE_URL,
  API_URL,
  WS_URL,
});
