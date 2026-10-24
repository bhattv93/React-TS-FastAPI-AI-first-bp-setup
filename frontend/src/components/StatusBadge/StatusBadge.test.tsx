import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  it.each([
    ['ok', 'bg-green-100'],
    ['error', 'bg-red-100'],
    ['loading', 'bg-gray-100'],
  ] as const)('renders the %s state', (status, expectedClass) => {
    render(<StatusBadge status={status} label={`label-${status}`} />);
    const badge = screen.getByRole('status');
    expect(badge).toHaveTextContent(`label-${status}`);
    expect(badge).toHaveClass(expectedClass);
  });
});
