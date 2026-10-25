import { render, type RenderResult } from '@testing-library/react';
import type { ReactElement } from 'react';

import { Providers } from './Providers';

/** Render a component inside a router and a no-retry query client. */
export function renderWithProviders(ui: ReactElement, route = '/'): RenderResult {
  return render(<Providers route={route}>{ui}</Providers>);
}
