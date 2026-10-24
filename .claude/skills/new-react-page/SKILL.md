---
name: new-react-page
description: Scaffold a React page with its route, data hook, service call, MSW handler and Testing Library test, following the page -> hook -> service -> client layering. Use when adding a screen or route in the frontend.
argument-hint: "[PageName]"
---

# New React page

**Canonical example to copy:** `frontend/src/pages/HomePage.tsx` with `frontend/src/hooks/useHealth.ts`,
`frontend/src/services/healthService.ts` and `frontend/src/pages/HomePage.test.tsx`.

## Steps

1. **Service** `src/services/<domain>Service.ts`: call the generated client, check `response.ok`, throw
   `toApiError(...)`. Run `just api-gen` first if the backend contract changed.
2. **Hook** `src/hooks/use<Domain>.ts`: wrap TanStack Query around the service. Components never import
   TanStack or services (ESLint enforces it).
3. **MSW handler** in `src/tests/handlers.ts` for each new endpoint.
4. **Test first** `src/pages/<Name>Page.test.tsx`: loading, success and error states; query by role or
   label; one test per acceptance criterion, titled `AC-n: ...`.
5. **Page** `src/pages/<Name>Page.tsx` using Tailwind utility classes and the shared components. Add the
   route to `src/routes.tsx`.
6. **Verify:** `just lint-frontend` and `just test-frontend`.

Keep components accessible: semantic elements, labelled inputs, `role="alert"` for errors, visible focus.
