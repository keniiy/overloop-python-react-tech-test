import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import AuthorCreate from '../../pages/Authors/AuthorCreate/AuthorCreate';
import { useAuthors } from '../../hooks/useAuthors';

// Mock the useAuthors hook
jest.mock('../../hooks/useAuthors');
const mockedUseAuthors = useAuthors;

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Test wrapper with Router
const TestWrapper = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('AuthorCreate', () => {
  const defaultMockHook = {
    createAuthor: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseAuthors.mockReturnValue(defaultMockHook);
  });

  describe('Rendering', () => {
    it('should render page header and navigation', () => {
      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      expect(screen.getByText('Create New Author')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /back to authors/i })).toBeInTheDocument();
    });

    it('should render AuthorForm with correct props', () => {
      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create author/i })).toBeInTheDocument();
    });

    it('should have correct back link URL', () => {
      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      const backLink = screen.getByRole('link', { name: /back to authors/i });
      expect(backLink).toHaveAttribute('href', '/authors/list');
    });
  });

  describe('Form Submission', () => {
    it('should handle successful author creation', async () => {
      const user = userEvent.setup();
      const mockCreateAuthor = jest.fn().mockResolvedValue({
        id: 1,
        first_name: 'John',
        last_name: 'Doe',
        full_name: 'John Doe'
      });

      mockedUseAuthors.mockReturnValue({
        createAuthor: mockCreateAuthor
      });

      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /create author/i });

      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockCreateAuthor).toHaveBeenCalledWith({
          first_name: 'John',
          last_name: 'Doe'
        });
      });

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/authors/list');
      });
    });

    it('should handle API errors', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Author already exists';
      const mockCreateAuthor = jest.fn().mockRejectedValue({
        response: { data: { error: errorMessage } }
      });

      mockedUseAuthors.mockReturnValue({
        createAuthor: mockCreateAuthor
      });

      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /create author/i });

      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });

      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('should handle network errors', async () => {
      const user = userEvent.setup();
      const mockCreateAuthor = jest.fn().mockRejectedValue(new Error('Network Error'));

      mockedUseAuthors.mockReturnValue({
        createAuthor: mockCreateAuthor
      });

      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /create author/i });

      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Network Error')).toBeInTheDocument();
      });
    });

    it('should handle generic errors', async () => {
      const user = userEvent.setup();
      const mockCreateAuthor = jest.fn().mockRejectedValue({});

      mockedUseAuthors.mockReturnValue({
        createAuthor: mockCreateAuthor
      });

      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /create author/i });

      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to create author')).toBeInTheDocument();
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading state during submission', async () => {
      const user = userEvent.setup();
      const mockCreateAuthor = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      mockedUseAuthors.mockReturnValue({
        createAuthor: mockCreateAuthor
      });

      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /create author/i });

      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.click(submitButton);

      // Should show loading spinner
      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });

    it('should disable form fields during loading', async () => {
      const user = userEvent.setup();
      const mockCreateAuthor = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      mockedUseAuthors.mockReturnValue({
        createAuthor: mockCreateAuthor
      });

      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /create author/i });

      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.click(submitButton);

      expect(firstNameInput).toBeDisabled();
      expect(lastNameInput).toBeDisabled();
    });
  });

  describe('Form Validation', () => {
    it('should not submit invalid form', async () => {
      const user = userEvent.setup();
      const mockCreateAuthor = jest.fn();

      mockedUseAuthors.mockReturnValue({
        createAuthor: mockCreateAuthor
      });

      render(
        <TestWrapper>
          <AuthorCreate />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /create author/i });
      await user.click(submitButton);

      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText(/first name is required/i)).toBeInTheDocument();
        expect(screen.getByText(/last name is required/i)).toBeInTheDocument();
      });

      expect(mockCreateAuthor).not.toHaveBeenCalled();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });
});