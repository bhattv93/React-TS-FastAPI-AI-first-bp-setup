import createClient from 'openapi-fetch';

import type { paths } from '../api/schema';
import { getConfig } from '../utils/config';

/** Typed API client generated from the backend's OpenAPI schema (`pnpm api:gen`). */
export function getApiClient() {
  return createClient<paths>({ baseUrl: getConfig().apiBaseUrl });
}
