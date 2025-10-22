import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

import AuthorCreate from '../../pages/Authors/AuthorCreate/AuthorCreate';
import { useAuthors } from '../../hooks/useAuthors';

jest.mock('../../hooks/useAuthors');
const mockedUseAuthors = useAuthors;

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

const renderComponent = () =>
  render(
    <MemoryRouter initialEntries={['/authors/create']}>
      <AuthorCreate />
    </MemoryRouter>
  );

describe('AuthorCreate', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const buildHookValue = (overrides = {}) => ({
    createAuthor: jest.fn().mockResolvedValue({
      id: 1,
      first_name: 'John',
      last_name: 'Doe',
      full_name: 'John Doe'
    }),
    ...overrides
  });

  it('renders header, back button, and form fields', () => {
    mockedUseAuthors.mockReturnValue(buildHookValue());

    renderComponent();

    expect(screen.getByText('Create New Author')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /back to authors/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
  });

  it('creates author and navigates back on success', async () => {
    const hookValue = buildHookValue();
    mockedUseAuthors.mockReturnValue(hookValue);
    const user = userEvent.setup();

    renderComponent();

    await user.type(screen.getByLabelText(/first name/i), 'Jane');
    await user.type(screen.getByLabelText(/last name/i), 'Smith');
    await user.click(screen.getByRole('button', { name: /create author/i }));

    await waitFor(() =>
      expect(hookValue.createAuthor).toHaveBeenCalledWith({
        first_name: 'Jane',
        last_name: 'Smith'
      })
    );
    expect(mockNavigate).toHaveBeenCalledWith('/authors/list');
  });

  it('shows API error message when creation fails', async () => {
    const hookValue = buildHookValue({
      createAuthor: jest.fn().mockRejectedValue({
        response: { data: { error: 'Author already exists' } }
      })
    });
    mockedUseAuthors.mockReturnValue(hookValue);
    const user = userEvent.setup();

    renderComponent();

    await user.type(screen.getByLabelText(/first name/i), 'Jane');
    await user.type(screen.getByLabelText(/last name/i), 'Smith');
    await user.click(screen.getByRole('button', { name: /create author/i }));

    await waitFor(() => {
      expect(screen.getByText('Author already exists')).toBeInTheDocument();
    });
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('shows network errors from createAuthor', async () => {
    const hookValue = buildHookValue({
      createAuthor: jest.fn().mockRejectedValue(new Error('Network Error'))
    });
    mockedUseAuthors.mockReturnValue(hookValue);
    const user = userEvent.setup();

    renderComponent();

    await user.type(screen.getByLabelText(/first name/i), 'Jane');
    await user.type(screen.getByLabelText(/last name/i), 'Smith');
    await user.click(screen.getByRole('button', { name: /create author/i }));

    await waitFor(() => {
      expect(screen.getByText('Network Error')).toBeInTheDocument();
    });
  });

  it('shows loading spinner while submitting', async () => {
    const hookValue = buildHookValue({
      createAuthor: jest.fn(() => new Promise((resolve) => setTimeout(resolve, 100)))
    });
    mockedUseAuthors.mockReturnValue(hookValue);
    const user = userEvent.setup();

    renderComponent();

    await user.type(screen.getByLabelText(/first name/i), 'Jane');
    await user.type(screen.getByLabelText(/last name/i), 'Smith');
    await user.click(screen.getByRole('button', { name: /create author/i }));

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create author/i })).toBeDisabled();
  });

  it('does not submit when form is invalid', async () => {
    const hookValue = buildHookValue({
      createAuthor: jest.fn()
    });
    mockedUseAuthors.mockReturnValue(hookValue);
    const user = userEvent.setup();

    renderComponent();

    await user.click(screen.getByRole('button', { name: /create author/i }));

    await waitFor(() => {
      expect(screen.getByText(/first name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/last name is required/i)).toBeInTheDocument();
    });

    expect(hookValue.createAuthor).not.toHaveBeenCalled();
  });
});
