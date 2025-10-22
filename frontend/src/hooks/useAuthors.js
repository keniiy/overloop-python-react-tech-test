import { useState, useCallback } from 'react';
import { authorsApi } from '../services/api/authors';
import { useNotification } from '../contexts/NotificationContext';
import { formatApiError } from '../utils/error';

// Custom hook for Authors following PROJECT_GUIDE.md structure
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
  const { showNotification } = useNotification();

  const fetchAuthors = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = await authorsApi.getAll();
      setAuthors(normaliseAuthorList(payload));
    } catch (err) {
      const message = formatApiError(err, 'Failed to fetch authors');
      setError(message);
      showNotification(message, 'error');
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const createAuthor = useCallback(async (authorData) => {
    try {
      const newAuthor = await authorsApi.create(authorData);
      setAuthors(prev => [...prev, newAuthor]);
      showNotification('Author created successfully', 'success');
      return newAuthor;
    } catch (err) {
      const message = formatApiError(err, 'Failed to create author');
      showNotification(message, 'error');
      err.formattedMessage = message;
      throw err;
    }
  }, [showNotification]);

  const updateAuthor = useCallback(async (id, authorData) => {
    try {
      const updatedAuthor = await authorsApi.update(id, authorData);
      setAuthors(prev => prev.map(author => 
        author.id === id ? updatedAuthor : author
      ));
      showNotification('Author updated successfully', 'success');
      return updatedAuthor;
    } catch (err) {
      const message = formatApiError(err, 'Failed to update author');
      showNotification(message, 'error');
      err.formattedMessage = message;
      throw err;
    }
  }, [showNotification]);

  const deleteAuthor = useCallback(async (id) => {
    try {
      await authorsApi.delete(id);
      setAuthors(prev => prev.filter(author => author.id !== id));
      showNotification('Author deleted successfully', 'success');
    } catch (err) {
      const message = formatApiError(err, 'Failed to delete author');
      showNotification(message, 'error');
      err.formattedMessage = message;
      throw err;
    }
  }, [showNotification]);

  const searchAuthors = useCallback(async (searchTerm) => {
    setLoading(true);
    setError(null);
    try {
      const payload = await authorsApi.search(searchTerm);
      setAuthors(normaliseAuthorList(payload));
    } catch (err) {
      const message = formatApiError(err, 'Failed to search authors');
      setError(message);
      showNotification(message, 'error');
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
    fetchAuthors,
    createAuthor,
    updateAuthor,
    deleteAuthor,
    searchAuthors,
    getAuthorById
  };
};
