import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

import AuthorView from '../../pages/Authors/AuthorView/AuthorView';
import { useAuthors } from '../../hooks/useAuthors';

jest.mock('../../hooks/useAuthors');

describe('AuthorView', () => {
  const setupMock = (overrides = {}) => {
    const defaults = {
      getAuthorById: jest.fn(),
    };
    useAuthors.mockReturnValue({ ...defaults, ...overrides });
    return { ...defaults, ...overrides };
  };

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderComponent = (authorId = '4') =>
    render(
      <MemoryRouter initialEntries={[`/authors/view/${authorId}`]}>
        <Routes>
          <Route path="/authors/view/:authorId" element={<AuthorView />} />
        </Routes>
      </MemoryRouter>
    );

  it('renders author details', async () => {
    const { getAuthorById } = setupMock({
      getAuthorById: jest.fn().mockResolvedValue({
        id: 4,
        first_name: 'Pat',
        last_name: 'Jones',
        full_name: 'Pat Jones',
      }),
    });

    renderComponent();

    await waitFor(() => expect(getAuthorById).toHaveBeenCalledWith('4'));

    expect(await screen.findByText('Pat Jones')).toBeInTheDocument();
    expect(await screen.findByText('Pat')).toBeInTheDocument();
    expect(await screen.findByText('Jones')).toBeInTheDocument();
  });

  it('shows error state', async () => {
    setupMock({
      getAuthorById: jest.fn().mockRejectedValue(new Error('Missing author')),
    });

    renderComponent();

    expect(await screen.findByText(/error loading author/i)).toBeInTheDocument();
    expect(await screen.findByText('Missing author')).toBeInTheDocument();
  });
});
