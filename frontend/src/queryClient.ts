import { QueryClient } from '@tanstack/react-query';

/** Production defaults for server-state caching. */
export function createQueryClient(): QueryClient {
  return new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } });
}
