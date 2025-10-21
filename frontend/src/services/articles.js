import client from './api/client';
import { API_ENDPOINTS } from '../config/api';

const formatArticlePayload = ({ title, content, authorId, regionIds }) => ({
  title,
  content,
  author_id: authorId ?? null,
  region_ids: Array.isArray(regionIds) ? regionIds : []
});

export const listArticles = async (params = {}) => {
  const {
    page = 1,
    limit = 10,
    search,
    authorId,
    regionId
  } = params;

  const response = await client.get(API_ENDPOINTS.ARTICLES, {
    params: {
      page,
      limit,
      ...(search ? { search } : {}),
      ...(authorId ? { author_id: authorId } : {}),
      ...(regionId ? { region_id: regionId } : {})
    }
  });

  return response.data;
};

export const getArticle = async (articleId) => {
  const response = await client.get(`${API_ENDPOINTS.ARTICLES}/${articleId}`);
  return response.data;
};

export const createArticle = async ({ title, content, authorId, regionIds }) => {
  const payload = formatArticlePayload({ title, content, authorId, regionIds });
  const response = await client.post(API_ENDPOINTS.ARTICLES, payload);
  return response.data;
};

export const editArticle = async (articleId, { title, content, authorId, regionIds }) => {
  const payload = formatArticlePayload({ title, content, authorId, regionIds });
  const response = await client.put(`${API_ENDPOINTS.ARTICLES}/${articleId}`, payload);
  return response.data;
};
