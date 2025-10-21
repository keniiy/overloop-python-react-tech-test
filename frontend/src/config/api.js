// API configuration following PROJECT_GUIDE.md structure
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';

export const API_ENDPOINTS = {
  // Articles
  ARTICLES: '/articles',

  // Authors (NEW)
  AUTHORS: '/authors',

  // Regions
  REGIONS: '/regions'
};

export const API_CONFIG = {
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
};