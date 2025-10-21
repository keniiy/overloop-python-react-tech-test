import { useState, useCallback } from 'react';
import { authorsApi } from '../services/api/authors';
import { useNotification } from '../contexts/NotificationContext';

// Custom hook for Authors following PROJECT_GUIDE.md structure
export const useAuthors = () => {
  const [authors, setAuthors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { showNotification } = useNotification();

  const fetchAuthors = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await authorsApi.getAll();
      setAuthors(data);
    } catch (err) {
      setError(err.message);
      showNotification('Failed to fetch authors', 'error');
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
      showNotification('Failed to create author', 'error');
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
      showNotification('Failed to update author', 'error');
      throw err;
    }
  }, [showNotification]);

  const deleteAuthor = useCallback(async (id) => {
    try {
      await authorsApi.delete(id);
      setAuthors(prev => prev.filter(author => author.id !== id));
      showNotification('Author deleted successfully', 'success');
    } catch (err) {
      showNotification('Failed to delete author', 'error');
      throw err;
    }
  }, [showNotification]);

  const searchAuthors = useCallback(async (searchTerm) => {
    setLoading(true);
    setError(null);
    try {
      const data = await authorsApi.search(searchTerm);
      setAuthors(data);
    } catch (err) {
      setError(err.message);
      showNotification('Failed to search authors', 'error');
    } finally {
      setLoading(false);
    }
  }, [showNotification]);

  const getAuthorById = useCallback(async (id) => {
    try {
      return await authorsApi.getById(id);
    } catch (err) {
      showNotification('Failed to fetch author', 'error');
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