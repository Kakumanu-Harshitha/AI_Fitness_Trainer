/**
 * API Configuration for React Web Frontend
 */

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8001';
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

console.log('[API] Configuration initialized:', {
  API_BASE_URL,
  API_URL,
  WS_URL,
});
