import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import AuthorEdit from '../../pages/Authors/AuthorEdit/AuthorEdit';
import { useAuthors } from '../../hooks/useAuthors';

// Mock the useAuthors hook
jest.mock('../../hooks/useAuthors');
const mockedUseAuthors = useAuthors;

// Mock useNavigate and useParams
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ id: '1' }),
}));

// Test wrapper with Router and specific route
const TestWrapper = ({ children, initialEntries = ['/authors/1'] }) => (
  <MemoryRouter initialEntries={initialEntries}>
    {children}
  </MemoryRouter>
);

describe('AuthorEdit', () => {
  const mockAuthor = {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    full_name: 'John Doe'
  };

  const defaultMockHook = {
    getAuthorById: jest.fn(),
    updateAuthor: jest.fn(),
    loading: false,
    error: null
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseAuthors.mockReturnValue(defaultMockHook);
  });

  describe('Rendering', () => {
    it('should render page header and navigation', async () => {
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Edit Author')).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /back to authors/i })).toBeInTheDocument();
      });
    });

    it('should fetch author data on mount', async () => {
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(defaultMockHook.getAuthorById).toHaveBeenCalledWith(1);
      });
    });

    it('should render AuthorForm with fetched data', async () => {
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByDisplayValue('John')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Doe')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /update author/i })).toBeInTheDocument();
      });
    });

    it('should have correct back link URL', async () => {
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        const backLink = screen.getByRole('link', { name: /back to authors/i });
        expect(backLink).toHaveAttribute('href', '/authors/list');
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading spinner while fetching author', () => {
      defaultMockHook.getAuthorById.mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText(/loading author/i)).toBeInTheDocument();
    });

    it('should show loading state during form submission', async () => {
      const user = userEvent.setup();
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        loading: true
      });

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /update author/i })).toBeDisabled();
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error when author not found', async () => {
      const errorMessage = 'Author not found';
      defaultMockHook.getAuthorById.mockRejectedValue(new Error(errorMessage));

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(`Error loading author: ${errorMessage}`)).toBeInTheDocument();
      });
    });

    it('should show error for invalid author ID', async () => {
      // Mock useParams to return invalid ID
      jest.doMock('react-router-dom', () => ({
        ...jest.requireActual('react-router-dom'),
        useNavigate: () => mockNavigate,
        useParams: () => ({ id: 'invalid' }),
      }));

      render(
        <TestWrapper initialEntries={['/authors/invalid']}>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Invalid author ID')).toBeInTheDocument();
      });
    });

    it('should display form error messages', async () => {
      const errorMessage = 'Author already exists';
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);
      
      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        error: errorMessage
      });

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    it('should handle successful author update', async () => {
      const user = userEvent.setup();
      const updatedAuthor = {
        id: 1,
        first_name: 'Jane',
        last_name: 'Smith',
        full_name: 'Jane Smith'
      };

      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);
      const mockUpdateAuthor = jest.fn().mockResolvedValue(updatedAuthor);

      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        updateAuthor: mockUpdateAuthor
      });

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByDisplayValue('John')).toBeInTheDocument();
      });

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /update author/i });

      await user.clear(firstNameInput);
      await user.clear(lastNameInput);
      await user.type(firstNameInput, 'Jane');
      await user.type(lastNameInput, 'Smith');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockUpdateAuthor).toHaveBeenCalledWith(1, {
          first_name: 'Jane',
          last_name: 'Smith'
        });
      });

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/authors/list');
      });
    });

    it('should handle API errors during update', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Author already exists';
      
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);
      const mockUpdateAuthor = jest.fn().mockRejectedValue({
        response: { data: { error: errorMessage } }
      });

      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        updateAuthor: mockUpdateAuthor
      });

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByDisplayValue('John')).toBeInTheDocument();
      });

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /update author/i });

      await user.clear(firstNameInput);
      await user.clear(lastNameInput);
      await user.type(firstNameInput, 'Jane');
      await user.type(lastNameInput, 'Smith');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });

      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('should handle network errors during update', async () => {
      const user = userEvent.setup();
      
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);
      const mockUpdateAuthor = jest.fn().mockRejectedValue(new Error('Network Error'));

      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        updateAuthor: mockUpdateAuthor
      });

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByDisplayValue('John')).toBeInTheDocument();
      });

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /update author/i });

      await user.clear(firstNameInput);
      await user.clear(lastNameInput);
      await user.type(firstNameInput, 'Jane');
      await user.type(lastNameInput, 'Smith');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Network Error')).toBeInTheDocument();
      });
    });

    it('should handle generic errors during update', async () => {
      const user = userEvent.setup();
      
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);
      const mockUpdateAuthor = jest.fn().mockRejectedValue({});

      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        updateAuthor: mockUpdateAuthor
      });

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByDisplayValue('John')).toBeInTheDocument();
      });

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /update author/i });

      await user.clear(firstNameInput);
      await user.clear(lastNameInput);
      await user.type(firstNameInput, 'Jane');
      await user.type(lastNameInput, 'Smith');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to update author')).toBeInTheDocument();
      });
    });
  });

  describe('Form Validation', () => {
    it('should not submit invalid form', async () => {
      const user = userEvent.setup();
      const mockUpdateAuthor = jest.fn();
      
      defaultMockHook.getAuthorById.mockResolvedValue(mockAuthor);

      mockedUseAuthors.mockReturnValue({
        ...defaultMockHook,
        updateAuthor: mockUpdateAuthor
      });

      render(
        <TestWrapper>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByDisplayValue('John')).toBeInTheDocument();
      });

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /update author/i });

      await user.clear(firstNameInput);
      await user.clear(lastNameInput);
      await user.click(submitButton);

      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText(/first name is required/i)).toBeInTheDocument();
        expect(screen.getByText(/last name is required/i)).toBeInTheDocument();
      });

      expect(mockUpdateAuthor).not.toHaveBeenCalled();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('URL Parameter Handling', () => {
    it('should handle different author IDs from URL params', async () => {
      // Test with different ID
      jest.doMock('react-router-dom', () => ({
        ...jest.requireActual('react-router-dom'),
        useNavigate: () => mockNavigate,
        useParams: () => ({ id: '5' }),
      }));

      defaultMockHook.getAuthorById.mockResolvedValue({
        id: 5,
        first_name: 'Alice',
        last_name: 'Johnson',
        full_name: 'Alice Johnson'
      });

      render(
        <TestWrapper initialEntries={['/authors/5']}>
          <AuthorEdit />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(defaultMockHook.getAuthorById).toHaveBeenCalledWith(5);
      });
    });
  });
});