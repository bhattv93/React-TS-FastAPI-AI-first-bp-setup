import { type QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { ReactNode } from 'react';
import { useLocation, useRoutes } from 'react-router-dom';

import { ErrorBoundary } from './components/ErrorBoundary';
import { routes } from './routes';

/** Route outlet. The router and query provider are supplied by `main.tsx` (and by tests). */
export function AppRoutes() {
  return useRoutes(routes);
}

/** Clears a displayed render error when the user navigates to another page. */
function RoutedErrorBoundary({ children }: { children: ReactNode }) {
  const { pathname } = useLocation();
  return <ErrorBoundary resetKey={pathname}>{children}</ErrorBoundary>;
}

export function App({ queryClient }: { queryClient: QueryClient }) {
  return (
    <RoutedErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AppRoutes />
      </QueryClientProvider>
    </RoutedErrorBoundary>
  );
}
