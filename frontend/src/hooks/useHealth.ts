import { useQuery } from '@tanstack/react-query';

import { fetchHealth } from '../services/healthService';

/** Server state for the API health check. Components use this hook, never TanStack directly. */
export function useHealth() {
  return useQuery({ queryKey: ['health'], queryFn: fetchHealth });
}
