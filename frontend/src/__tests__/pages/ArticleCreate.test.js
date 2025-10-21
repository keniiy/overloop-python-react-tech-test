import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

import ArticleCreate from '../../pages/Articles/ArticleCreate/ArticleCreate';
import { useAuthors } from '../../hooks/useAuthors';
import { createArticle } from '../../services/articles';

jest.mock('../../hooks/useAuthors');
jest.mock('../../services/articles', () => ({
  ...jest.requireActual('../../services/articles'),
  createArticle: jest.fn()
}));

jest.mock('../../components/RegionDropdown/RegionDropdown', () => ({
  __esModule: true,
  default: ({ onChange }) => (
    <button type="button" onClick={() => onChange([{ id: 1, name: 'Europe' }])}>
      Select Region
    </button>
  )
}));

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

describe('ArticleCreate', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const setupAuthorsMock = (overrides = {}) => {
    const defaults = {
      authors: [
        { id: 1, first_name: 'John', last_name: 'Doe', full_name: 'John Doe' },
        { id: 2, first_name: 'Jane', last_name: 'Smith', full_name: 'Jane Smith' }
      ],
      fetchAuthors: jest.fn(),
      loading: false,
      error: null
    };

    useAuthors.mockReturnValue({ ...defaults, ...overrides });
    return { ...defaults, ...overrides };
  };

  const renderComponent = () =>
    render(
      <MemoryRouter>
        <ArticleCreate />
      </MemoryRouter>
    );

  it('loads authors on mount', async () => {
    const { fetchAuthors } = setupAuthorsMock();

    renderComponent();

    await waitFor(() => {
      expect(fetchAuthors).toHaveBeenCalledTimes(1);
    });
  });

  it('submits article with selected author and regions', async () => {
    setupAuthorsMock();
    createArticle.mockResolvedValue({ id: 10 });
    const user = userEvent.setup();

    renderComponent();

    await user.type(screen.getByLabelText(/title/i), 'New Article');
    await user.type(screen.getByLabelText(/content/i), 'Some interesting content that is long enough.');
    await user.selectOptions(screen.getByLabelText(/author/i), '1');
    await user.click(screen.getByRole('button', { name: /select region/i }));
    await user.click(screen.getByRole('button', { name: /save article/i }));

    await waitFor(() => {
      expect(createArticle).toHaveBeenCalledWith({
        title: 'New Article',
        content: 'Some interesting content that is long enough.',
        authorId: 1,
        regionIds: [1]
      });
    });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/articles/list');
    });
  });

  it('shows API errors when creation fails', async () => {
    setupAuthorsMock();
    const errorMessage = 'Validation failed';
    createArticle.mockRejectedValue(new Error(errorMessage));
    const user = userEvent.setup();

    renderComponent();

    await user.type(screen.getByLabelText(/title/i), 'New Article');
    await user.type(screen.getByLabelText(/content/i), 'Some interesting content that is long enough.');
    await user.click(screen.getByRole('button', { name: /save article/i }));

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
