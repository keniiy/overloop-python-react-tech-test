import { useState, useCallback, useRef } from 'react';
import { authorsApi } from '../services/api/authors';
import { useNotification } from '../contexts/NotificationContext';
import { formatApiError } from '../utils/error';

const DEFAULT_QUERY = {
  page: 1,
  limit: 10,
};

const DEFAULT_PAGINATION = {
  current_page: 1,
  per_page: DEFAULT_QUERY.limit,
  total_items: 0,
  total_pages: 1,
  has_next: false,
  has_prev: false,
  next_page: null,
  prev_page: null,
};

const normaliseAuthorList = (payload) => {
  if (Array.isArray(payload)) {
    return payload;
  }
  if (payload?.data && Array.isArray(payload.data)) {
    return payload.data;
  }
  return [];
};

export const useAuthors = () => {
  const [authors, setAuthors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState(DEFAULT_PAGINATION);
  const { showNotification } = useNotification();
  const queryRef = useRef(DEFAULT_QUERY);

  const fetchAuthors = useCallback(async (params = {}) => {
    const effectiveParams = {
      page: params.page ?? queryRef.current.page ?? DEFAULT_QUERY.page,
      limit: params.limit ?? queryRef.current.limit ?? DEFAULT_QUERY.limit,
    };

    if (params.search !== undefined) {
      if (params.search === null || params.search === '') {
        effectiveParams.search = undefined;
      } else {
        effectiveParams.search = params.search;
      }
    } else if (queryRef.current.search !== undefined) {
      effectiveParams.search = queryRef.current.search;
    }

    setLoading(true);
    setError(null);
    try {
      const payload = await authorsApi.getAll(effectiveParams);
      const list = normaliseAuthorList(payload);
      setAuthors(list);

      if (payload?.pagination) {
        setPagination(payload.pagination);
      } else {
        setPagination({
          ...DEFAULT_PAGINATION,
          current_page: effectiveParams.page,
          per_page: effectiveParams.limit,
          total_items: list.length,
          total_pages: Math.max(1, Math.ceil(list.length / effectiveParams.limit)),
        });
      }

      queryRef.current = {
        ...effectiveParams,
        ...(effectiveParams.search ? { search: effectiveParams.search } : {}),
      };

      return payload;
    } catch (err) {
      const message = formatApiError(err, 'Failed to fetch authors');
      setError(message);
      showNotification(message, 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const createAuthor = useCallback(async (authorData) => {
    try {
      const newAuthor = await authorsApi.create(authorData);
      showNotification('Author created successfully', 'success');
      await fetchAuthors(queryRef.current);
      return newAuthor;
    } catch (err) {
      const message = formatApiError(err, 'Failed to create author');
      showNotification(message, 'error');
      err.formattedMessage = message;
      throw err;
    }
  }, [fetchAuthors, showNotification]);

  const updateAuthor = useCallback(async (id, authorData) => {
    try {
      const updatedAuthor = await authorsApi.update(id, authorData);
      showNotification('Author updated successfully', 'success');
      await fetchAuthors(queryRef.current);
      return updatedAuthor;
    } catch (err) {
      const message = formatApiError(err, 'Failed to update author');
      showNotification(message, 'error');
      err.formattedMessage = message;
      throw err;
    }
  }, [fetchAuthors, showNotification]);

  const deleteAuthor = useCallback(async (id) => {
    try {
      await authorsApi.delete(id);
      showNotification('Author deleted successfully', 'success');

      const current = queryRef.current;
      const isLastItemOnPage = authors.length === 1;
      const nextPage = isLastItemOnPage && pagination.has_prev
        ? Math.max(1, (current.page ?? 1) - 1)
        : current.page;

      await fetchAuthors({ ...current, page: nextPage });
    } catch (err) {
      const message = formatApiError(err, 'Failed to delete author');
      showNotification(message, 'error');
      err.formattedMessage = message;
      throw err;
    }
  }, [authors.length, fetchAuthors, pagination.has_prev, showNotification]);

  const searchAuthors = useCallback(async (searchTerm) => {
    setLoading(true);
    setError(null);
    try {
      const payload = await authorsApi.search(searchTerm, {
        page: 1,
        limit: queryRef.current.limit ?? DEFAULT_QUERY.limit,
      });
      const list = normaliseAuthorList(payload);
      setAuthors(list);

      if (payload?.pagination) {
        setPagination(payload.pagination);
      } else {
        setPagination({
          ...DEFAULT_PAGINATION,
          current_page: 1,
          per_page: queryRef.current.limit ?? DEFAULT_QUERY.limit,
          total_items: list.length,
          total_pages: Math.max(1, Math.ceil(list.length / (queryRef.current.limit ?? DEFAULT_QUERY.limit))),
        });
      }

      queryRef.current = {
        page: 1,
        limit: queryRef.current.limit ?? DEFAULT_QUERY.limit,
        ...(searchTerm ? { search: searchTerm } : {}),
      };
    } catch (err) {
      const message = formatApiError(err, 'Failed to search authors');
      setError(message);
      showNotification(message, 'error');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const getAuthorById = useCallback(async (id) => {
    try {
      return await authorsApi.getById(id);
    } catch (err) {
      const message = formatApiError(err, 'Failed to fetch author');
      showNotification(message, 'error');
      err.formattedMessage = message;
      throw err;
    }
  }, [showNotification]);

  return {
    authors,
    loading,
    error,
    pagination,
    fetchAuthors,
    createAuthor,
    updateAuthor,
    deleteAuthor,
    searchAuthors,
    getAuthorById,
  };
};
