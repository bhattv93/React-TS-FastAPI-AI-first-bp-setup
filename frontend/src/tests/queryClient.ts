import { QueryClient } from '@tanstack/react-query';

/** A query client that never retries, so failing requests surface immediately in tests. */
export function createTestQueryClient(): QueryClient {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}
