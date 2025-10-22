import { listArticles, getArticle, createArticle, editArticle } from '../../services/articles';
import client from '../../services/api/client';

jest.mock('../../services/api/client', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
}));

describe('articles service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('lists articles with query params', async () => {
    const response = { data: [], pagination: {} };
    client.get.mockResolvedValue({ data: response });

    const result = await listArticles({ page: 2, limit: 5, search: 'hello', authorId: 1, regionId: 3 });

    expect(client.get).toHaveBeenCalledWith('/articles', {
      params: {
        page: 2,
        limit: 5,
        search: 'hello',
        author_id: 1,
        region_id: 3,
      },
    });
    expect(result).toEqual(response);
  });

  it('gets article by id', async () => {
    const article = { id: 1 };
    client.get.mockResolvedValue({ data: article });

    const result = await getArticle(1);
    expect(client.get).toHaveBeenCalledWith('/articles/1');
    expect(result).toEqual(article);
  });

  it('creates article with formatted payload', async () => {
    const payload = {
      title: 'Test',
      content: 'Some content',
      authorId: 5,
      regionIds: [1, 2],
    };
    const created = { id: 10 };
    client.post.mockResolvedValue({ data: created });

    const result = await createArticle(payload);

    expect(client.post).toHaveBeenCalledWith('/articles', {
      title: 'Test',
      content: 'Some content',
      author_id: 5,
      region_ids: [1, 2],
    });
    expect(result).toEqual(created);
  });

  it('allows creating article without author or regions', async () => {
    client.post.mockResolvedValue({ data: {} });

    await createArticle({ title: 'T', content: 'C', authorId: null, regionIds: null });

    expect(client.post).toHaveBeenCalledWith('/articles', {
      title: 'T',
      content: 'C',
      author_id: null,
      region_ids: [],
    });
  });

  it('edits article with formatted payload', async () => {
    client.put.mockResolvedValue({ data: {} });

    await editArticle(3, { title: 'Updated', content: 'New content', authorId: undefined, regionIds: [] });

    expect(client.put).toHaveBeenCalledWith('/articles/3', {
      title: 'Updated',
      content: 'New content',
      author_id: null,
      region_ids: [],
    });
  });
});
