import { type QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useRoutes } from 'react-router-dom';

import { ErrorBoundary } from './components/ErrorBoundary';
import { routes } from './routes';

/** Route outlet. The router and query provider are supplied by `main.tsx` (and by tests). */
export function AppRoutes() {
  return useRoutes(routes);
}

export function App({ queryClient }: { queryClient: QueryClient }) {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AppRoutes />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
