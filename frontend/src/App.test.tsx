import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { App } from './App';
import { createQueryClient } from './queryClient';
import { createTestQueryClient } from './tests/queryClient';

function renderApp(route: string) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <App queryClient={createTestQueryClient()} />
    </MemoryRouter>,
  );
}

describe('App routing', () => {
  it('renders the home page at /', async () => {
    renderApp('/');
    expect(await screen.findByRole('heading', { name: 'AI-First App' })).toBeInTheDocument();
    expect(await screen.findByText('API is healthy')).toBeInTheDocument();
  });

  it('renders the not-found page for unknown routes and links home', () => {
    renderApp('/nope');
    expect(screen.getByRole('heading', { name: 'Page not found' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Back to home' })).toHaveAttribute('href', '/');
  });
});

describe('createQueryClient', () => {
  it('uses production caching defaults', () => {
    const options = createQueryClient().getDefaultOptions().queries;
    expect(options).toMatchObject({ staleTime: 30_000, retry: 1 });
  });
});
