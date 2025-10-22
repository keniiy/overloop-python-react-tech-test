import { formatApiError, collectDetailMessages } from '../../utils/error';

describe('error utilities', () => {
  it('collects nested detail messages', () => {
    const detail = {
      msg: 'Top level',
      details: [
        'Simple error',
        { msg: 'Second level' },
        { details: [{ msg: 'Deep message' }] },
      ],
    };

    expect(collectDetailMessages(detail)).toEqual([
      'Top level',
      'Simple error',
      'Second level',
      'Deep message',
    ]);
  });

  it('formats API error with details', () => {
    const error = {
      response: {
        data: {
          error: 'Validation failed',
          details: [
            {
              msg: 'String should have at least 5 characters',
            },
            {
              details: [
                { msg: 'Title is required' },
              ],
            },
          ],
        },
      },
    };

    expect(formatApiError(error)).toBe(
      'Validation failed | String should have at least 5 characters | Title is required'
    );
  });

  it('falls back to error message when no response data', () => {
    const error = new Error('Network failure');
    expect(formatApiError(error)).toBe('Network failure');
  });

  it('falls back to default message when nothing provided', () => {
    expect(formatApiError(null, 'Default')).toBe('Default');
  });
});
