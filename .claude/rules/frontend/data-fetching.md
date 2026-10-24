---
paths:
  - "frontend/src/hooks/**"
  - "frontend/src/services/**"
---

# Data fetching (ADR-0005)

- `services/<domain>Service.ts` wraps the generated client (`getApiClient()`), checks `response.ok`, and
  throws `toApiError(...)`. No React imports.
- `hooks/use<Domain>.ts` wraps TanStack Query (`useQuery` / `useMutation`) around the service. Components
  never use TanStack directly.
- Query keys are arrays starting with the domain name (`['items', filters]`). Invalidate by domain after a
  mutation.
- Read the API origin from `getConfig().apiBaseUrl`; never hard-code it.
- Add an MSW handler for each new endpoint in `src/tests/handlers.ts` so tests stay offline.
