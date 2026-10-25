import type { components } from '../api/schema';
import { getApiClient } from './client';
import { toApiError } from './errors';

export type HealthResponse = components['schemas']['HealthResponse'];

/** Call `GET /api/v1/health`. */
export async function fetchHealth(): Promise<HealthResponse> {
  const { data, error, response } = await getApiClient().GET('/api/v1/health');
  if (!response.ok || data === undefined) {
    throw toApiError(response.status, error);
  }
  return data;
}
