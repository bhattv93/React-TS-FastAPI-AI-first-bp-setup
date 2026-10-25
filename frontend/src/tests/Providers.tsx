import { type QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { MemoryRouter } from 'react-router-dom';

import { createTestQueryClient } from './queryClient';

export function Providers({
  children,
  route = '/',
  client = createTestQueryClient(),
}: {
  children: ReactNode;
  route?: string;
  client?: QueryClient;
}) {
  return (
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[route]}>{children}</MemoryRouter>
    </QueryClientProvider>
  );
}
