---
paths:
  - "frontend/src/**/*.ts"
  - "frontend/src/**/*.tsx"
---

# TypeScript and React

- TypeScript `strict` plus `noUncheckedIndexedAccess`. Avoid `any`; use `unknown` and narrow.
- Function components with a typed `Props` interface; named exports; one component per file.
- Layering is enforced by ESLint: page -> hook -> service -> generated client. Components and pages never
  import `services/` or `api/`; `utils/` imports no React.
- Style with Tailwind utility classes. No runtime CSS-in-JS.
- Accessible by default: semantic elements, labelled controls, `role="alert"` for errors.
- Show errors with `getErrorMessage()`. API errors carry a request ID worth surfacing.
- Never edit `src/api/schema.d.ts` (generated). Never put secrets in the frontend.
