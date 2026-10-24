import { describe, expect, it } from 'vitest';

import { getErrorMessage } from './errors';

describe('getErrorMessage', () => {
  it('returns the message of an Error', () => {
    expect(getErrorMessage(new Error('boom'))).toBe('boom');
  });

  it('appends the request id when the error carries one', () => {
    const error = Object.assign(new Error('boom'), { requestId: 'abc' });
    expect(getErrorMessage(error)).toBe('boom (ref abc)');
  });

  it('falls back for non-Error values', () => {
    expect(getErrorMessage('text')).toBe('Something went wrong');
  });
});
