import { renderHook, act } from '@testing-library/react';
import { useAuthors } from '../../hooks/useAuthors';
import { NotificationProvider } from '../../contexts/NotificationContext';
import { authorsApi } from '../../services/api/authors';

// Mock the authors API
jest.mock('../../services/api/authors');
const mockedAuthorsApi = authorsApi;

// Test wrapper with NotificationProvider
const wrapper = ({ children }) => (
  <NotificationProvider>{children}</NotificationProvider>
);

describe('useAuthors', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('fetchAuthors', () => {
    it('should fetch authors successfully', async () => {
      const mockAuthors = [
        { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' },
        { id: 2, first_name: 'Jane', last_name: 'Smith', full_name: 'Jane Smith' }
      ];
      
      mockedAuthorsApi.getAll.mockResolvedValue(mockAuthors);

      const { result } = renderHook(() => useAuthors(), { wrapper });

      expect(result.current.loading).toBe(false);
      expect(result.current.authors).toEqual([]);
      expect(result.current.error).toBe(null);

      await act(async () => {
        await result.current.fetchAuthors();
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.authors).toEqual(mockAuthors);
      expect(result.current.error).toBe(null);
      expect(mockedAuthorsApi.getAll).toHaveBeenCalledTimes(1);
    });

    it('should handle fetch errors', async () => {
      const errorMessage = 'Network Error';
      mockedAuthorsApi.getAll.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useAuthors(), { wrapper });

      await act(async () => {
        await result.current.fetchAuthors();
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.authors).toEqual([]);
      expect(result.current.error).toBe(errorMessage);
    });

    it('should set loading state correctly', async () => {
      mockedAuthorsApi.getAll.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve([]), 100))
      );

      const { result } = renderHook(() => useAuthors(), { wrapper });

      act(() => {
        result.current.fetchAuthors();
      });

      expect(result.current.loading).toBe(true);
    });
  });

  describe('createAuthor', () => {
    it('should create author successfully', async () => {
      const newAuthorData = { first_name: 'Bob', last_name: 'Johnson' };
      const createdAuthor = { id: 3, ...newAuthorData, full_name: 'Bob Johnson' };
      
      mockedAuthorsApi.create.mockResolvedValue(createdAuthor);

      const { result } = renderHook(() => useAuthors(), { wrapper });

      let returnedAuthor;
      await act(async () => {
        returnedAuthor = await result.current.createAuthor(newAuthorData);
      });

      expect(result.current.authors).toContain(createdAuthor);
      expect(returnedAuthor).toEqual(createdAuthor);
      expect(mockedAuthorsApi.create).toHaveBeenCalledWith(newAuthorData);
    });

    it('should handle create errors', async () => {
      const newAuthorData = { first_name: '', last_name: 'Johnson' };
      const createError = new Error('Validation failed');
      
      mockedAuthorsApi.create.mockRejectedValue(createError);

      const { result } = renderHook(() => useAuthors(), { wrapper });

      await expect(act(async () => {
        await result.current.createAuthor(newAuthorData);
      })).rejects.toThrow('Validation failed');

      expect(result.current.authors).toEqual([]);
    });
  });

  describe('updateAuthor', () => {
    it('should update author successfully', async () => {
      const existingAuthors = [
        { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' }
      ];
      const updateData = { first_name: 'Jane', last_name: 'Doe' };
      const updatedAuthor = { id: 1, ...updateData, full_name: 'Jane Doe' };
      
      mockedAuthorsApi.update.mockResolvedValue(updatedAuthor);

      const { result } = renderHook(() => useAuthors(), { wrapper });
      
      // Set initial authors
      act(() => {
        result.current.authors.push(...existingAuthors);
      });

      await act(async () => {
        await result.current.updateAuthor(1, updateData);
      });

      expect(result.current.authors).toContainEqual(updatedAuthor);
      expect(mockedAuthorsApi.update).toHaveBeenCalledWith(1, updateData);
    });
  });

  describe('deleteAuthor', () => {
    it('should delete author successfully', async () => {
      const existingAuthors = [
        { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' },
        { id: 2, first_name: 'Jane', last_name: 'Smith', full_name: 'Jane Smith' }
      ];
      
      mockedAuthorsApi.delete.mockResolvedValue({ message: 'Author deleted successfully' });

      const { result } = renderHook(() => useAuthors(), { wrapper });
      
      // Manually set initial state for this test
      act(() => {
        result.current.authors.splice(0, result.current.authors.length, ...existingAuthors);
      });

      await act(async () => {
        await result.current.deleteAuthor(1);
      });

      expect(result.current.authors).not.toContainEqual(existingAuthors[0]);
      expect(result.current.authors).toHaveLength(1);
      expect(mockedAuthorsApi.delete).toHaveBeenCalledWith(1);
    });
  });

  describe('searchAuthors', () => {
    it('should search authors successfully', async () => {
      const searchResults = [
        { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' }
      ];
      
      mockedAuthorsApi.search.mockResolvedValue(searchResults);

      const { result } = renderHook(() => useAuthors(), { wrapper });

      await act(async () => {
        await result.current.searchAuthors('John');
      });

      expect(result.current.authors).toEqual(searchResults);
      expect(mockedAuthorsApi.search).toHaveBeenCalledWith('John');
    });
  });

  describe('getAuthorById', () => {
    it('should get author by ID successfully', async () => {
      const mockAuthor = { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' };
      
      mockedAuthorsApi.getById.mockResolvedValue(mockAuthor);

      const { result } = renderHook(() => useAuthors(), { wrapper });

      let returnedAuthor;
      await act(async () => {
        returnedAuthor = await result.current.getAuthorById(1);
      });

      expect(returnedAuthor).toEqual(mockAuthor);
      expect(mockedAuthorsApi.getById).toHaveBeenCalledWith(1);
    });
  });
});