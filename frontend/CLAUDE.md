# Frontend (React + TypeScript)

Design reference: `docs/02-architecture/frontend.md`. Run `just` recipes from the repository root, or
`pnpm ...` from this folder.

## Layout (`src/`)

- `pages/`: route screens. Compose components and hooks; never call services or the client.
- `components/<Name>/`: reusable UI (`Name.tsx`, `Name.test.tsx`, `index.ts`). Data arrives through props.
- `hooks/use<Domain>.ts`: the only code that calls `services/`. Wrap TanStack Query here, never in components.
- `services/`: thin wrappers over the generated client (`getApiClient()`). No React imports.
- `api/`: **generated** (`openapi.json`, `schema.d.ts`). Never hand-edit; run `just api-gen`.
- `utils/`: pure helpers, including runtime config (`config.ts`). No React or services.
- `tests/`: shared test setup, MSW handlers, `renderWithProviders`.
- ESLint enforces these boundaries with `no-restricted-imports`.

## Conventions

- TypeScript `strict` plus `noUncheckedIndexedAccess`. Avoid `any`; use `unknown` and narrow.
- Function components with typed props. Named exports. One component per file.
- Style with Tailwind utility classes. No runtime CSS-in-JS.
- Accessibility: semantic elements; query tests by role or label (`getByRole`), not test ids.
- Runtime config comes from `/config.json` (`apiBaseUrl`, `env`), loaded before render. Never put secrets in
  the frontend; only `VITE_*` build constants are exposed.
- API errors use the backend envelope; show them with `getErrorMessage()`.

## Tests

- Vitest + React Testing Library + MSW. Co-locate `*.test.tsx` with the code.
- Default MSW handlers are in `src/tests/handlers.ts`; override per test with `server.use(...)`.
- Unhandled network requests fail the test on purpose.
- Coverage thresholds are 80% (lines, branches, functions, statements) in `vitest.config.ts`.

## Tooling notes

- TypeScript is pinned to 5.9.x (`openapi-typescript` peer) and ESLint to 9.x (`eslint-plugin-jsx-a11y` peer).
  `strictPeerDependencies` is on; do not use overrides to get around it. See
  `docs/07-engineering-process/vulnerability-management.md` for when to revisit.
- Add dependencies with `pnpm add`; never edit `pnpm-lock.yaml` by hand.
