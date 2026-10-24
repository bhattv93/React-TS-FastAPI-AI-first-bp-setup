import { screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';

import { TEST_API } from '../tests/handlers';
import { renderWithProviders } from '../tests/renderWithProviders';
import { server } from '../tests/server';
import { HomePage } from './HomePage';

describe('HomePage', () => {
  it('shows a loading state, then the healthy API version', async () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText('Checking API...')).toBeInTheDocument();
    expect(await screen.findByText('API is healthy')).toBeInTheDocument();
    expect(screen.getByText('Version 1.2.3 (test)')).toBeInTheDocument();
  });

  it('shows an accessible error with the request id when the API fails', async () => {
    server.use(
      http.get(`${TEST_API}/api/v1/health`, () =>
        HttpResponse.json(
          {
            error: {
              code: 'internal_error',
              message: 'Internal server error',
              request_id: 'rid-9',
            },
          },
          { status: 500 },
        ),
      ),
    );
    renderWithProviders(<HomePage />);
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('API unreachable');
    expect(alert).toHaveTextContent('Internal server error (ref rid-9)');
  });
});
