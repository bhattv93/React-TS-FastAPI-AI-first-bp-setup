import { renderHook, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { describe, expect, it } from 'vitest';

import { Providers } from '../tests/Providers';
import { useHealth } from './useHealth';

function wrapper({ children }: { children: ReactNode }) {
  return <Providers>{children}</Providers>;
}

describe('useHealth', () => {
  it('starts pending and resolves with the health payload', async () => {
    const { result } = renderHook(() => useHealth(), { wrapper });
    expect(result.current.isPending).toBe(true);
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
    expect(result.current.data?.version).toBe('1.2.3');
  });
});
