import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

import ArticleList from '../../pages/Articles/ArticleList/ArticleList';
import { listArticles } from '../../services/articles';

jest.mock('../../services/articles', () => ({
  ...jest.requireActual('../../services/articles'),
  listArticles: jest.fn()
}));

describe('ArticleList', () => {
  const renderComponent = () =>
    render(
      <MemoryRouter>
        <ArticleList />
      </MemoryRouter>
    );

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders articles with author and regions', async () => {
    listArticles.mockResolvedValueOnce({
      data: [
        {
          id: 1,
          title: 'Article One',
          author: { id: 2, full_name: 'Jane Smith', first_name: 'Jane', last_name: 'Smith' },
          regions: [{ id: 10, name: 'EMEA' }]
        }
      ],
      pagination: {
        current_page: 1,
        total_pages: 1,
        total_items: 1,
        per_page: 10,
        has_next: false,
        has_prev: false
      }
    });

    renderComponent();

    await waitFor(() => expect(listArticles).toHaveBeenCalledWith({ page: 1, limit: 10 }));
    await waitFor(() => expect(screen.queryByText(/loading articles/i)).not.toBeInTheDocument());

    expect(screen.getByText('Article One')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('EMEA')).toBeInTheDocument();
    expect(screen.getByText(/page 1 of 1/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /view/i })).toHaveAttribute('href', '/articles/view/1');
  });

  it('shows placeholder when no articles exist', async () => {
    listArticles.mockResolvedValueOnce({
      data: [],
      pagination: {
        current_page: 1,
        total_pages: 1,
        total_items: 0,
        per_page: 10,
        has_next: false,
        has_prev: false
      }
    });

    renderComponent();

    await waitFor(() => expect(listArticles).toHaveBeenCalled());
    await waitFor(() => expect(screen.queryByText(/loading articles/i)).not.toBeInTheDocument());

    expect(screen.getByText(/no articles found/i)).toBeInTheDocument();
  });

  it('paginates to next page', async () => {
    listArticles
      .mockResolvedValueOnce({
        data: [
          { id: 1, title: 'Article One', author: null, regions: [] }
        ],
        pagination: {
          current_page: 1,
          total_pages: 2,
          total_items: 2,
          per_page: 10,
          has_next: true,
          has_prev: false
        }
      })
      .mockResolvedValueOnce({
        data: [
          { id: 2, title: 'Article Two', author: null, regions: [] }
        ],
        pagination: {
          current_page: 2,
          total_pages: 2,
          total_items: 2,
          per_page: 10,
          has_next: false,
          has_prev: true
        }
      });

    const user = userEvent.setup();

    renderComponent();

    await waitFor(() => expect(listArticles).toHaveBeenCalledWith({ page: 1, limit: 10 }));
    await waitFor(() => expect(screen.queryByText(/loading articles/i)).not.toBeInTheDocument());

    await user.click(screen.getByRole('button', { name: /next/i }));

    await waitFor(() => expect(listArticles).toHaveBeenLastCalledWith({ page: 2, limit: 10 }));
    await waitFor(() => expect(screen.queryByText(/loading articles/i)).not.toBeInTheDocument());
    expect(screen.getByText('Article Two')).toBeInTheDocument();
  });

  it('shows error when API call fails', async () => {
    listArticles.mockRejectedValueOnce(new Error('Network error'));

    renderComponent();

    await waitFor(() => expect(screen.getByText('Network error')).toBeInTheDocument());
  });
});
