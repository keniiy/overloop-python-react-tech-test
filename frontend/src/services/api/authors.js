import client from './client';
import { API_ENDPOINTS } from '../../config/api';

// Authors API service following PROJECT_GUIDE.md structure
export const authorsApi = {
  // Get all authors
  getAll: async () => {
    const response = await client.get(API_ENDPOINTS.AUTHORS);
    return response.data;
  },

  // Get author by ID
  getById: async (id) => {
    const response = await client.get(`${API_ENDPOINTS.AUTHORS}/${id}`);
    return response.data;
  },

  // Create new author
  create: async (authorData) => {
    const response = await client.post(API_ENDPOINTS.AUTHORS, authorData);
    return response.data;
  },

  // Update existing author
  update: async (id, authorData) => {
    const response = await client.put(`${API_ENDPOINTS.AUTHORS}/${id}`, authorData);
    return response.data;
  },

  // Delete author
  delete: async (id) => {
    const response = await client.delete(`${API_ENDPOINTS.AUTHORS}/${id}`);
    return response.data;
  },

  // Search authors
  search: async (searchTerm) => {
    const response = await client.get(`${API_ENDPOINTS.AUTHORS}/search`, {
      params: { q: searchTerm }
    });
    return response.data;
  },

  // Get authors with statistics
  getWithStats: async () => {
    const response = await client.get(`${API_ENDPOINTS.AUTHORS}/with-stats`);
    return response.data;
  }
};