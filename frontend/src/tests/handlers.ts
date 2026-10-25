import { http, HttpResponse } from 'msw';

export const TEST_API = 'http://localhost';

/** Default happy-path handlers. Individual tests override them with `server.use(...)`. */
export const handlers = [
  http.get(`${TEST_API}/api/v1/health`, () =>
    HttpResponse.json({ status: 'ok', version: '1.2.3', env: 'test' }),
  ),
];
