import React from 'react';
import { render, screen, waitFor, waitForElementToBeRemoved } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';

import ArticleEdit from '../../pages/Articles/ArticleEdit/ArticleEdit';
import { useAuthors } from '../../hooks/useAuthors';
import { getArticle, editArticle } from '../../services/articles';

jest.mock('../../hooks/useAuthors');
jest.mock('../../services/articles', () => ({
  ...jest.requireActual('../../services/articles'),
  getArticle: jest.fn(),
  editArticle: jest.fn()
}));

jest.mock('../../components/RegionDropdown/RegionDropdown', () => ({
  __esModule: true,
  default: ({ onChange }) => (
    <button type="button" onClick={() => onChange([{ id: 2, name: 'Asia' }])}>
      Update Regions
    </button>
  )
}));

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ articleId: '5' })
}));

describe('ArticleEdit', () => {
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
        <ArticleEdit />
      </MemoryRouter>
    );

  it('loads article data and authors on mount', async () => {
    const { fetchAuthors } = setupAuthorsMock();
    getArticle.mockResolvedValue({
      id: 5,
      title: 'Existing Article',
      content: 'Existing article content',
      author_id: 2,
      regions: [{ id: 1, name: 'Europe' }]
    });

    renderComponent();

    await waitFor(() => expect(getArticle).toHaveBeenCalledWith('5'));
    await waitForElementToBeRemoved(() => screen.getByText(/loading article details/i));

    expect(screen.getByDisplayValue('Existing Article')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Existing article content')).toBeInTheDocument();
    expect(fetchAuthors).toHaveBeenCalledTimes(1);
    expect(screen.getByRole('combobox')).toHaveValue('2');
  });

  it('updates article and navigates back on success', async () => {
    setupAuthorsMock();
    getArticle.mockResolvedValue({
      id: 5,
      title: 'Existing Article',
      content: 'Existing article content',
      author_id: 1,
      regions: [{ id: 3, name: 'North America' }]
    });
    editArticle.mockResolvedValue({ id: 5 });
    const user = userEvent.setup();

    renderComponent();

    await waitFor(() => expect(getArticle).toHaveBeenCalled());
    await waitForElementToBeRemoved(() => screen.getByText(/loading article details/i));

    await user.clear(screen.getByLabelText(/title/i));
    await user.type(screen.getByLabelText(/title/i), 'Updated Article');
    await user.selectOptions(screen.getByLabelText(/author/i), '2');
    await user.click(screen.getByRole('button', { name: /update regions/i }));
    await user.click(screen.getByRole('button', { name: /save article/i }));

    await waitFor(() =>
      expect(editArticle).toHaveBeenCalledWith('5', {
        title: 'Updated Article',
        content: 'Existing article content',
        authorId: 2,
        regionIds: [2]
      })
    );

    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/articles/list'));
  });

  it('shows error message when update fails', async () => {
    setupAuthorsMock();
    getArticle.mockResolvedValue({
      id: 5,
      title: 'Existing Article',
      content: 'Existing article content',
      author_id: null,
      regions: []
    });
    editArticle.mockRejectedValue(new Error('Update failed'));
    const user = userEvent.setup();

    renderComponent();

    await waitFor(() => expect(getArticle).toHaveBeenCalled());
    await waitForElementToBeRemoved(() => screen.getByText(/loading article details/i));

    await user.click(screen.getByRole('button', { name: /save article/i }));

    await waitFor(() => expect(screen.getByText('Update failed')).toBeInTheDocument());
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('shows alert when article fails to load', async () => {
    setupAuthorsMock();
    getArticle.mockRejectedValue(new Error('Not found'));

    renderComponent();

    await waitFor(() => expect(screen.getByText(/error loading article/i)).toBeInTheDocument());
  });
});
