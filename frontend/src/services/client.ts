import createClient from 'openapi-fetch';

import type { paths } from '../api/schema';
import { getConfig } from '../utils/config';

type ApiClient = ReturnType<typeof createClient<paths>>;

let cached: { baseUrl: string; client: ApiClient } | undefined;

/**
 * Typed API client generated from the backend's OpenAPI schema (`pnpm api:gen`).
 *
 * One client is shared per API base URL, so middleware registered on it (auth, request IDs)
 * applies to every call.
 */
export function getApiClient(): ApiClient {
  const { apiBaseUrl } = getConfig();
  if (cached?.baseUrl !== apiBaseUrl) {
    cached = { baseUrl: apiBaseUrl, client: createClient<paths>({ baseUrl: apiBaseUrl }) };
  }
  return cached.client;
}
