import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

import ArticleView from '../../pages/Articles/ArticleView/ArticleView';
import { getArticle } from '../../services/articles';

jest.mock('../../services/articles', () => ({
  ...jest.requireActual('../../services/articles'),
  getArticle: jest.fn(),
}));

describe('ArticleView', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderComponent = (articleId = '5') =>
    render(
      <MemoryRouter initialEntries={[`/articles/view/${articleId}`]}>
        <Routes>
          <Route path="/articles/view/:articleId" element={<ArticleView />} />
        </Routes>
      </MemoryRouter>
    );

  it('renders article details', async () => {
    getArticle.mockResolvedValue({
      id: 5,
      title: 'Article Title',
      content: 'The body',
      author: { first_name: 'Ann', last_name: 'Lee' },
      regions: [{ id: 1, name: 'EMEA' }],
    });

    renderComponent();

    await waitFor(() => expect(getArticle).toHaveBeenCalledWith('5'));
    expect(screen.getByText('Article Title')).toBeInTheDocument();
    expect(screen.getByText(/ann lee/i)).toBeInTheDocument();
    expect(screen.getByText('EMEA')).toBeInTheDocument();
  });

  it('shows error state', async () => {
    getArticle.mockRejectedValue(new Error('Not found'));

    renderComponent();

    await waitFor(() => expect(screen.getByText(/error loading article/i)).toBeInTheDocument());
    expect(screen.getByText('Not found')).toBeInTheDocument();
  });
});
