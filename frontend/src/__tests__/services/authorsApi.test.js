import { authorsApi } from '../../services/api/authors';
import client from '../../services/api/client';

// Mock the API client
jest.mock('../../services/api/client');
const mockedClient = client;

describe('authorsApi', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should fetch all authors successfully', async () => {
      const mockAuthors = [
        { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' },
        { id: 2, first_name: 'Jane', last_name: 'Smith', full_name: 'Jane Smith' }
      ];
      
      mockedClient.get.mockResolvedValue({ data: mockAuthors });

      const result = await authorsApi.getAll();

      expect(mockedClient.get).toHaveBeenCalledWith('/authors', {
        params: { page: undefined, limit: undefined }
      });
      expect(result).toEqual(mockAuthors);
    });

    it('should handle API errors', async () => {
      const errorMessage = 'Network Error';
      mockedClient.get.mockRejectedValue(new Error(errorMessage));

      await expect(authorsApi.getAll()).rejects.toThrow(errorMessage);
    });
  });

  describe('getById', () => {
    it('should fetch author by ID successfully', async () => {
      const mockAuthor = { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' };
      mockedClient.get.mockResolvedValue({ data: mockAuthor });

      const result = await authorsApi.getById(1);

      expect(mockedClient.get).toHaveBeenCalledWith('/authors/1');
      expect(result).toEqual(mockAuthor);
    });
  });

  describe('create', () => {
    it('should create author successfully', async () => {
      const newAuthor = { first_name: 'John', last_name: 'Doe' };
      const createdAuthor = { id: 1, ...newAuthor, full_name: 'John Doe' };
      
      mockedClient.post.mockResolvedValue({ data: createdAuthor });

      const result = await authorsApi.create(newAuthor);

      expect(mockedClient.post).toHaveBeenCalledWith('/authors', newAuthor);
      expect(result).toEqual(createdAuthor);
    });

    it('should handle validation errors', async () => {
      const invalidAuthor = { first_name: '', last_name: 'Doe' };
      const validationError = {
        response: { 
          status: 400, 
          data: { error: 'Validation failed', details: ['First name is required'] }
        }
      };
      
      mockedClient.post.mockRejectedValue(validationError);

      await expect(authorsApi.create(invalidAuthor)).rejects.toEqual(validationError);
    });
  });

  describe('update', () => {
    it('should update author successfully', async () => {
      const authorId = 1;
      const updateData = { first_name: 'Jane', last_name: 'Smith' };
      const updatedAuthor = { id: authorId, ...updateData, full_name: 'Jane Smith' };
      
      mockedClient.put.mockResolvedValue({ data: updatedAuthor });

      const result = await authorsApi.update(authorId, updateData);

      expect(mockedClient.put).toHaveBeenCalledWith('/authors/1', updateData);
      expect(result).toEqual(updatedAuthor);
    });
  });

  describe('delete', () => {
    it('should delete author successfully', async () => {
      const authorId = 1;
      const deleteResponse = { message: 'Author deleted successfully' };
      
      mockedClient.delete.mockResolvedValue({ data: deleteResponse });

      const result = await authorsApi.delete(authorId);

      expect(mockedClient.delete).toHaveBeenCalledWith('/authors/1');
      expect(result).toEqual(deleteResponse);
    });

    it('should handle delete errors for authors with articles', async () => {
      const authorId = 1;
      const deleteError = {
        response: { 
          status: 400, 
          data: { error: 'Cannot delete author who has written articles' }
        }
      };
      
      mockedClient.delete.mockRejectedValue(deleteError);

      await expect(authorsApi.delete(authorId)).rejects.toEqual(deleteError);
    });
  });

  describe('search', () => {
    it('should search authors successfully', async () => {
      const searchTerm = 'John';
      const searchResults = [
        { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' }
      ];
      
      mockedClient.get.mockResolvedValue({ data: searchResults });

      const result = await authorsApi.search(searchTerm);

      expect(mockedClient.get).toHaveBeenCalledWith('/authors', {
        params: { page: undefined, limit: undefined, search: searchTerm }
      });
      expect(result).toEqual(searchResults);
    });

    it('should return empty array for no search results', async () => {
      const searchTerm = 'NonExistent';
      mockedClient.get.mockResolvedValue({ data: [] });

      const result = await authorsApi.search(searchTerm);

      expect(mockedClient.get).toHaveBeenCalledWith('/authors', {
        params: { page: undefined, limit: undefined, search: searchTerm }
      });
      expect(result).toEqual([]);
    });
  });

  describe('getWithStats', () => {
    it('should fetch authors with statistics successfully', async () => {
      const authorsWithStats = [
        { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe', article_count: 3 },
        { id: 2, first_name: 'Jane', last_name: 'Smith', full_name: 'Jane Smith', article_count: 1 }
      ];
      
      mockedClient.get.mockResolvedValue({ data: authorsWithStats });

      const result = await authorsApi.getWithStats();

      expect(mockedClient.get).toHaveBeenCalledWith('/authors/with-stats');
      expect(result).toEqual(authorsWithStats);
    });
  });
});
