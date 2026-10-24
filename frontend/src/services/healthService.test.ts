import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';

import { server } from '../tests/server';
import { TEST_API } from '../tests/handlers';
import { ApiError } from './errors';
import { fetchHealth } from './healthService';

describe('fetchHealth', () => {
  it('returns the typed health payload', async () => {
    await expect(fetchHealth()).resolves.toEqual({ status: 'ok', version: '1.2.3', env: 'test' });
  });

  it('throws an ApiError built from the backend envelope', async () => {
    server.use(
      http.get(`${TEST_API}/api/v1/health`, () =>
        HttpResponse.json(
          { error: { code: 'not_ready', message: 'Database is not reachable', request_id: 'r1' } },
          { status: 503 },
        ),
      ),
    );
    await expect(fetchHealth()).rejects.toMatchObject({
      name: 'ApiError',
      status: 503,
      code: 'not_ready',
      requestId: 'r1',
    });
    await expect(fetchHealth()).rejects.toBeInstanceOf(ApiError);
  });
});
