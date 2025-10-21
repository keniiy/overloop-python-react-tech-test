import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AuthorForm from '../../components/forms/AuthorForm/AuthorForm';

describe('AuthorForm', () => {
  const defaultProps = {
    onSubmit: jest.fn(),
    loading: false,
    error: null,
    submitText: 'Save Author'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render form with all fields', () => {
      render(<AuthorForm {...defaultProps} />);

      expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /save author/i })).toBeInTheDocument();
    });

    it('should render with initial data', () => {
      const initialData = { first_name: 'John', last_name: 'Doe' };
      
      render(
        <AuthorForm 
          {...defaultProps} 
          initialData={initialData}
        />
      );

      expect(screen.getByDisplayValue('John')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Doe')).toBeInTheDocument();
    });

    it('should render custom submit text', () => {
      render(
        <AuthorForm 
          {...defaultProps} 
          submitText="Create Author"
        />
      );

      expect(screen.getByRole('button', { name: /create author/i })).toBeInTheDocument();
    });

    it('should display error message', () => {
      const errorMessage = 'Failed to save author';
      
      render(
        <AuthorForm 
          {...defaultProps} 
          error={errorMessage}
        />
      );

      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should update form fields when user types', async () => {
      const user = userEvent.setup();
      render(<AuthorForm {...defaultProps} />);

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);

      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');

      expect(firstNameInput).toHaveValue('John');
      expect(lastNameInput).toHaveValue('Doe');
    });

    it('should clear validation errors when user starts typing', async () => {
      const user = userEvent.setup();
      render(<AuthorForm {...defaultProps} />);

      const submitButton = screen.getByRole('button', { name: /save author/i });
      const firstNameInput = screen.getByLabelText(/first name/i);

      // Submit empty form to trigger validation
      await user.click(submitButton);
      
      // Check validation error appears
      await waitFor(() => {
        expect(screen.getByText(/first name is required/i)).toBeInTheDocument();
      });

      // Start typing to clear error
      await user.type(firstNameInput, 'J');

      // Validation error should be cleared
      await waitFor(() => {
        expect(screen.queryByText(/first name is required/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Form Validation', () => {
    it('should show validation errors for empty fields', async () => {
      const user = userEvent.setup();
      render(<AuthorForm {...defaultProps} />);

      const submitButton = screen.getByRole('button', { name: /save author/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/first name is required/i)).toBeInTheDocument();
        expect(screen.getByText(/last name is required/i)).toBeInTheDocument();
      });

      // onSubmit should not be called for invalid form
      expect(defaultProps.onSubmit).not.toHaveBeenCalled();
    });

    it('should show validation errors for short names', async () => {
      const user = userEvent.setup();
      render(<AuthorForm {...defaultProps} />);

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /save author/i });

      await user.type(firstNameInput, 'J');
      await user.type(lastNameInput, 'D');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/first name must be at least 2 characters/i)).toBeInTheDocument();
        expect(screen.getByText(/last name must be at least 2 characters/i)).toBeInTheDocument();
      });

      expect(defaultProps.onSubmit).not.toHaveBeenCalled();
    });

    it('should validate whitespace-only input', async () => {
      const user = userEvent.setup();
      render(<AuthorForm {...defaultProps} />);

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /save author/i });

      await user.type(firstNameInput, '   ');
      await user.type(lastNameInput, '   ');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/first name is required/i)).toBeInTheDocument();
        expect(screen.getByText(/last name is required/i)).toBeInTheDocument();
      });

      expect(defaultProps.onSubmit).not.toHaveBeenCalled();
    });
  });

  describe('Form Submission', () => {
    it('should submit valid form data', async () => {
      const user = userEvent.setup();
      const mockOnSubmit = jest.fn();
      
      render(
        <AuthorForm 
          {...defaultProps} 
          onSubmit={mockOnSubmit}
        />
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /save author/i });

      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          first_name: 'John',
          last_name: 'Doe'
        });
      });
    });

    it('should trim whitespace from submitted data', async () => {
      const user = userEvent.setup();
      const mockOnSubmit = jest.fn();
      
      render(
        <AuthorForm 
          {...defaultProps} 
          onSubmit={mockOnSubmit}
        />
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const submitButton = screen.getByRole('button', { name: /save author/i });

      await user.type(firstNameInput, '  John  ');
      await user.type(lastNameInput, '  Doe  ');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          first_name: 'John',
          last_name: 'Doe'
        });
      });
    });
  });

  describe('Loading State', () => {
    it('should disable form when loading', () => {
      render(
        <AuthorForm 
          {...defaultProps} 
          loading={true}
        />
      );

      expect(screen.getByLabelText(/first name/i)).toBeDisabled();
      expect(screen.getByLabelText(/last name/i)).toBeDisabled();
      expect(screen.getByRole('button', { name: /save author/i })).toBeDisabled();
    });

    it('should show loading spinner when loading', () => {
      render(
        <AuthorForm 
          {...defaultProps} 
          loading={true}
        />
      );

      expect(screen.getByRole('status')).toBeInTheDocument();
    });
  });

  describe('Keyboard Navigation', () => {
    it('should submit form on Enter key', async () => {
      const user = userEvent.setup();
      const mockOnSubmit = jest.fn();
      
      render(
        <AuthorForm 
          {...defaultProps} 
          onSubmit={mockOnSubmit}
        />
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);

      await user.type(firstNameInput, 'John');
      await user.type(lastNameInput, 'Doe');
      await user.keyboard('{Enter}');

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          first_name: 'John',
          last_name: 'Doe'
        });
      });
    });
  });
});