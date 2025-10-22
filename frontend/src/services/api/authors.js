import client from './client';
import { API_ENDPOINTS } from '../../config/api';

const mapSearchParam = (search) => {
  if (search === undefined || search === null) {
    return {};
  }
  const trimmed = String(search).trim();
  return trimmed.length > 0 ? { search: trimmed } : {};
};

// Authors API service following PROJECT_GUIDE.md structure
export const authorsApi = {
  // Get all authors (supports pagination + search)
  getAll: async (params = {}) => {
    const response = await client.get(API_ENDPOINTS.AUTHORS, {
      params: {
        page: params.page,
        limit: params.limit,
        ...mapSearchParam(params.search)
      }
    });
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

  // Search authors (delegates to getAll with search param)
  search: async (searchTerm, params = {}) => {
    return authorsApi.getAll({
      ...params,
      search: searchTerm
    });
  },

  // Get authors with statistics
  getWithStats: async () => {
    const response = await client.get(`${API_ENDPOINTS.AUTHORS}/with-stats`);
    return response.data;
  }
};
