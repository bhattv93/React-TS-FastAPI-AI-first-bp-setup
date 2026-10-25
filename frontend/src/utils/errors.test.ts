import { describe, expect, it } from 'vitest';

import { ApiError } from '../services/errors';
import { ConfigError } from './config';
import { getErrorMessage, UserFacingError } from './errors';

describe('getErrorMessage', () => {
  it('shows the message of an error written for users', () => {
    expect(getErrorMessage(new UserFacingError('Please sign in'))).toBe('Please sign in');
    expect(getErrorMessage(new ConfigError('config.json is missing'))).toBe(
      'config.json is missing',
    );
  });

  it('appends the request id of an API error', () => {
    const error = new ApiError('Internal server error', 500, 'internal_error', 'abc');
    expect(getErrorMessage(error)).toBe('Internal server error (ref abc)');
  });

  it('hides the message of unexpected errors', () => {
    expect(getErrorMessage(new TypeError('Failed to fetch'))).toBe('Something went wrong');
    expect(getErrorMessage(new Error('SELECT * FROM users failed'))).toBe('Something went wrong');
  });

  it('falls back for non-Error values', () => {
    expect(getErrorMessage('text')).toBe('Something went wrong');
  });
});
