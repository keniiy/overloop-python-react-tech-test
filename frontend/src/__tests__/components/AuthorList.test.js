import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import AuthorList from '../../pages/Authors/AuthorList/AuthorList';
import { useAuthors } from '../../hooks/useAuthors';

// Mock the useAuthors hook
jest.mock('../../hooks/useAuthors');
const mockedUseAuthors = useAuthors;

// Mock window.confirm
Object.defineProperty(window, 'confirm', {
  writable: true,
  value: jest.fn(),
});

// Test wrapper with Router
const TestWrapper = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('AuthorList', () => {
  const defaultMockHook = {
    authors: [],
    loading: false,
    error: null,
    fetchAuthors: jest.fn(),
    deleteAuthor: jest.fn(),
    searchAuthors: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    window.confirm.mockReturnValue(true);
    mockedUseAuthors.mockReturnValue(defaultMockHook);
  });

  describe('Rendering', () => {
    it('should render page header and add button', () => {
      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      expect(screen.getByText('Authors')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /add new author/i })).toBeInTheDocument();
    });

    it('should render search form', () => {
      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      expect(screen.getByPlaceholderText(/search authors by name/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
    });

    it('should call fetchAuthors on mount', () => {
      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      expect(defaultMockHook.fetchAuthors).toHaveBeenCalledTimes(1);
    });
  });

  describe('Loading State', () => {
    it('should show loading spinner when loading', () => {
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        loading: true
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    it('should show error message when there is an error', () => {
      const errorMessage = 'Failed to fetch authors';
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        error: errorMessage
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      expect(screen.getByText(`Error loading authors: ${errorMessage}`)).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('should show empty state message when no authors', () => {
      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      expect(screen.getByText(/no authors found/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /add the first author/i })).toBeInTheDocument();
    });

    it('should show search-specific empty state message', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/search authors by name/i);
      const searchButton = screen.getByRole('button', { name: /search/i });

      await user.type(searchInput, 'NonExistent');
      await user.click(searchButton);

      expect(screen.getByText(/no authors found.*try a different search term/i)).toBeInTheDocument();
    });
  });

  describe('Authors Table', () => {
    const mockAuthors = [
      { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' },
      { id: 2, first_name: 'Jane', last_name: 'Smith', full_name: 'Jane Smith' }
    ];

    it('should render authors table with data', () => {
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        authors: mockAuthors
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      // Check table headers
      expect(screen.getByText('ID')).toBeInTheDocument();
      expect(screen.getByText('Name')).toBeInTheDocument();
      expect(screen.getByText('First Name')).toBeInTheDocument();
      expect(screen.getByText('Last Name')).toBeInTheDocument();
      expect(screen.getByText('Actions')).toBeInTheDocument();

      // Check author data
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Doe')).toBeInTheDocument();
    });

    it('should show author count', () => {
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        authors: mockAuthors
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      expect(screen.getByText('Showing 2 authors')).toBeInTheDocument();
    });

    it('should show singular count for one author', () => {
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        authors: [mockAuthors[0]]
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      expect(screen.getByText('Showing 1 author')).toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    it('should handle search form submission', async () => {
      const user = userEvent.setup();
      const mockSearchAuthors = jest.fn();
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        searchAuthors: mockSearchAuthors
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/search authors by name/i);
      const searchButton = screen.getByRole('button', { name: /search/i });

      await user.type(searchInput, 'John');
      await user.click(searchButton);

      expect(mockSearchAuthors).toHaveBeenCalledWith('John');
    });

    it('should handle search form submission with Enter key', async () => {
      const user = userEvent.setup();
      const mockSearchAuthors = jest.fn();
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        searchAuthors: mockSearchAuthors
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/search authors by name/i);

      await user.type(searchInput, 'John');
      await user.keyboard('{Enter}');

      expect(mockSearchAuthors).toHaveBeenCalledWith('John');
    });

    it('should handle clear search', async () => {
      const user = userEvent.setup();
      const mockFetchAuthors = jest.fn();
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        fetchAuthors: mockFetchAuthors
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/search authors by name/i);
      const clearButton = screen.getByRole('button', { name: /clear/i });

      await user.type(searchInput, 'John');
      await user.click(clearButton);

      expect(searchInput).toHaveValue('');
      expect(mockFetchAuthors).toHaveBeenCalledTimes(2); // Once on mount, once on clear
    });

    it('should fetch all authors when searching with empty term', async () => {
      const user = userEvent.setup();
      const mockFetchAuthors = jest.fn();
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        fetchAuthors: mockFetchAuthors
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const searchButton = screen.getByRole('button', { name: /search/i });
      await user.click(searchButton);

      expect(mockFetchAuthors).toHaveBeenCalledTimes(2); // Once on mount, once on empty search
    });
  });

  describe('Delete Functionality', () => {
    const mockAuthors = [
      { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' }
    ];

    it('should handle delete confirmation', async () => {
      const user = userEvent.setup();
      const mockDeleteAuthor = jest.fn();
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        authors: mockAuthors,
        deleteAuthor: mockDeleteAuthor
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const deleteButton = screen.getByRole('button', { name: /delete/i });
      await user.click(deleteButton);

      expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete John Doe?');
      expect(mockDeleteAuthor).toHaveBeenCalledWith(1);
    });

    it('should not delete when user cancels confirmation', async () => {
      const user = userEvent.setup();
      const mockDeleteAuthor = jest.fn();
      window.confirm.mockReturnValue(false);
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        authors: mockAuthors,
        deleteAuthor: mockDeleteAuthor
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const deleteButton = screen.getByRole('button', { name: /delete/i });
      await user.click(deleteButton);

      expect(window.confirm).toHaveBeenCalled();
      expect(mockDeleteAuthor).not.toHaveBeenCalled();
    });

    it('should handle delete errors gracefully', async () => {
      const user = userEvent.setup();
      const mockDeleteAuthor = jest.fn().mockRejectedValue(new Error('Delete failed'));
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        authors: mockAuthors,
        deleteAuthor: mockDeleteAuthor
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const deleteButton = screen.getByRole('button', { name: /delete/i });
      await user.click(deleteButton);

      // Should not throw error - error handling is done in the hook
      expect(mockDeleteAuthor).toHaveBeenCalledWith(1);
    });
  });

  describe('Navigation Links', () => {
    it('should have correct edit links', () => {
      const mockAuthors = [
        { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' }
      ];
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        authors: mockAuthors
      });

      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const editButton = screen.getByRole('button', { name: /edit/i });
      expect(editButton).toHaveAttribute('href', '/authors/1');
    });

    it('should have correct add new author link', () => {
      render(
        <TestWrapper>
          <AuthorList />
        </TestWrapper>
      );

      const addButton = screen.getByRole('button', { name: /add new author/i });
      expect(addButton).toHaveAttribute('href', '/authors/create');
    });
  });
});
