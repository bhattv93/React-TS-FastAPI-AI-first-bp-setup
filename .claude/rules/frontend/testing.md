---
paths:
  - "frontend/**/*.test.ts"
  - "frontend/**/*.test.tsx"
  - "frontend/src/tests/**"
---

# Frontend tests

- Vitest + React Testing Library + MSW. Co-locate `Name.test.tsx` with the code.
- Query by role or label (`getByRole`), not test IDs. Use `userEvent` for interaction.
- Render with `renderWithProviders` (router + a no-retry query client). Override handlers per test with
  `server.use(...)`; unhandled network requests fail the test on purpose.
- Name the test after the acceptance criterion it proves, for example `it('AC-1: lists only shipped items')`.
- Thresholds are 80% for lines, branches, functions and statements. Never lower them or exclude files to
  pass; write the missing test.
