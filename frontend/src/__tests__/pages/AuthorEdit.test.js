import React from 'react';
import { render, screen, waitFor, waitForElementToBeRemoved } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

import AuthorEdit from '../../pages/Authors/AuthorEdit/AuthorEdit';
import { useAuthors } from '../../hooks/useAuthors';

jest.mock('../../hooks/useAuthors');
const mockedUseAuthors = useAuthors;

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ authorId: '1' })
}));

const renderComponent = () =>
  render(
    <MemoryRouter initialEntries={['/authors/1']}>
      <AuthorEdit />
    </MemoryRouter>
  );

describe('AuthorEdit', () => {
  const mockAuthor = {
    id: 1,
    first_name: 'John',
    last_name: 'Doe',
    full_name: 'John Doe'
  };

  const buildHookValue = (overrides = {}) => ({
    getAuthorById: jest.fn().mockResolvedValue(mockAuthor),
    updateAuthor: jest.fn().mockResolvedValue({ ...mockAuthor }),
    ...overrides
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('loads author details and renders form', async () => {
    const hookValue = buildHookValue();
    mockedUseAuthors.mockReturnValue(hookValue);

    renderComponent();

    expect(screen.getByText(/loading author details/i)).toBeInTheDocument();

    await waitForElementToBeRemoved(() => screen.getByText(/loading author details/i));

    expect(hookValue.getAuthorById).toHaveBeenCalledWith('1');
    expect(screen.getByDisplayValue('John')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Doe')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /update author/i })).toBeInTheDocument();
  });

  it('shows error message when loading fails', async () => {
    const hookValue = buildHookValue({
      getAuthorById: jest.fn().mockRejectedValue(new Error('Author not found'))
    });
    mockedUseAuthors.mockReturnValue(hookValue);

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText(/error loading author/i)).toBeInTheDocument();
      expect(screen.getByText('Author not found')).toBeInTheDocument();
    });
  });

  it('updates author and navigates back on success', async () => {
    const hookValue = buildHookValue();
    mockedUseAuthors.mockReturnValue(hookValue);
    const user = userEvent.setup();

    renderComponent();
    await waitForElementToBeRemoved(() => screen.getByText(/loading author details/i));

    await user.clear(screen.getByLabelText(/first name/i));
    await user.type(screen.getByLabelText(/first name/i), 'Jane');
    await user.clear(screen.getByLabelText(/last name/i));
    await user.type(screen.getByLabelText(/last name/i), 'Smith');
    await user.click(screen.getByRole('button', { name: /update author/i }));

    await waitFor(() =>
      expect(hookValue.updateAuthor).toHaveBeenCalledWith('1', {
        first_name: 'Jane',
        last_name: 'Smith'
      })
    );
    expect(mockNavigate).toHaveBeenCalledWith('/authors/list');
  });

  it('shows submit error when update fails', async () => {
    const hookValue = buildHookValue({
      updateAuthor: jest.fn().mockRejectedValue({
        response: { data: { error: 'Author already exists' } }
      })
    });
    mockedUseAuthors.mockReturnValue(hookValue);
    const user = userEvent.setup();

    renderComponent();
    await waitForElementToBeRemoved(() => screen.getByText(/loading author details/i));

    await user.click(screen.getByRole('button', { name: /update author/i }));

    await waitFor(() => {
      expect(screen.getByText('Author already exists')).toBeInTheDocument();
    });
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('handles network errors during update gracefully', async () => {
    const hookValue = buildHookValue({
      updateAuthor: jest.fn().mockRejectedValue(new Error('Network Error'))
    });
    mockedUseAuthors.mockReturnValue(hookValue);
    const user = userEvent.setup();

    renderComponent();
    await waitForElementToBeRemoved(() => screen.getByText(/loading author details/i));

    await user.click(screen.getByRole('button', { name: /update author/i }));

    await waitFor(() => {
      expect(screen.getByText('Network Error')).toBeInTheDocument();
    });
  });
});
