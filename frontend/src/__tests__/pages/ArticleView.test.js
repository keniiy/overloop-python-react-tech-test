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

    expect(await screen.findByText('Article Title')).toBeInTheDocument();
    expect(await screen.findByText(/ann lee/i)).toBeInTheDocument();
    expect(await screen.findByText('EMEA')).toBeInTheDocument();
  });

  it('shows error state', async () => {
    getArticle.mockRejectedValue(new Error('Not found'));

    renderComponent();

    expect(await screen.findByText(/error loading article/i)).toBeInTheDocument();
    expect(await screen.findByText('Not found')).toBeInTheDocument();
  });
});
