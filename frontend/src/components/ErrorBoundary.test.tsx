import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { ErrorBoundary } from './ErrorBoundary';

function Bomb(): never {
  throw new Error('kaboom');
}

function ThrowsUndefined(): never {
  // eslint-disable-next-line @typescript-eslint/only-throw-error
  throw undefined;
}

function Flaky({ fail }: { fail: boolean }) {
  if (fail) {
    throw new Error('kaboom');
  }
  return <p>recovered</p>;
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders children when nothing fails', () => {
    render(
      <ErrorBoundary>
        <p>all good</p>
      </ErrorBoundary>,
    );
    expect(screen.getByText('all good')).toBeInTheDocument();
  });

  it('shows an accessible fallback without leaking the raw error message', () => {
    render(
      <ErrorBoundary>
        <Bomb />
      </ErrorBoundary>,
    );
    expect(screen.getByRole('alert')).toHaveTextContent('Something went wrong.');
    expect(screen.queryByText(/kaboom/)).not.toBeInTheDocument();
  });

  it('still shows the fallback when the thrown value is undefined', () => {
    render(
      <ErrorBoundary>
        <ThrowsUndefined />
      </ErrorBoundary>,
    );
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('recovers when the reset key changes, for example after navigating away', () => {
    const { rerender } = render(
      <ErrorBoundary resetKey="/a">
        <Flaky fail />
      </ErrorBoundary>,
    );
    expect(screen.getByRole('alert')).toBeInTheDocument();

    rerender(
      <ErrorBoundary resetKey="/a">
        <Flaky fail={false} />
      </ErrorBoundary>,
    );
    expect(screen.getByRole('alert')).toBeInTheDocument();

    rerender(
      <ErrorBoundary resetKey="/b">
        <Flaky fail={false} />
      </ErrorBoundary>,
    );
    expect(screen.getByText('recovered')).toBeInTheDocument();
  });
});
