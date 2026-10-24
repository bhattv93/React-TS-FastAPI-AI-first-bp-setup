import { describe, expect, it } from 'vitest';

import { ApiError, toApiError } from './errors';

describe('toApiError', () => {
  it('reads code, message and request id from the backend envelope', () => {
    const error = toApiError(404, {
      error: { code: 'not_found', message: 'Item 7 not found', request_id: 'rid-1' },
    });
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({
      status: 404,
      code: 'not_found',
      message: 'Item 7 not found',
      requestId: 'rid-1',
    });
  });

  it('falls back when the body is not an envelope', () => {
    const error = toApiError(502, '<html>Bad gateway</html>');
    expect(error).toMatchObject({
      status: 502,
      code: 'unknown',
      message: 'Request failed (HTTP 502)',
    });
    expect(error.requestId).toBeUndefined();
  });

  it('falls back field by field when the envelope is incomplete', () => {
    const error = toApiError(500, { error: { code: 5 } });
    expect(error).toMatchObject({ code: 'unknown', message: 'Request failed (HTTP 500)' });
  });
});
