---
status: accepted
owner: tech-lead
last-reviewed: 2026-10-24
---

# ADR-0005: Server-state management on the frontend: TanStack Query behind hooks

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

The frontend talks to FastAPI through a typed client generated from OpenAPI (`openapi-typescript` +
`openapi-fetch`, see [frontend.md](../02-architecture/frontend.md#api-client)). We needed to decide how
components fetch data, cache it, retry, and invalidate after mutations.

## Decision

Use **TanStack Query**, **wrapped**: components never call it directly. They call per-domain hooks in
`src/hooks/` (for example `useItems()`), which wrap `useQuery` / `useMutation` around the typed client in
`src/services/`. If we ever drop TanStack, only the hooks change.

## Alternatives considered

| Option | Pros | Cons |
|--------|------|------|
| **A. TanStack Query (chosen)** | Caching, dedup, retries, loading/error states, invalidation, devtools; one uniform pattern for AI to generate and test | Extra dependency and concepts (query keys, staleTime) |
| B. Custom hooks over the typed client | No dependency | We re-implement caching, retry and invalidation, and each hook drifts |
| C. React Router loaders/actions | Data tied to routes | Weak for shared or background data; mixes routing and data concerns |

## Consequences

- One documented pattern keeps AI-generated hooks and tests consistent.
- Tests wrap components in a `QueryClientProvider` (`renderWithProviders`) with retries disabled.
- `frontend/CLAUDE.md`, `.claude/rules/frontend/data-fetching.md` and the `new-react-page` skill describe the
  hook pattern.
