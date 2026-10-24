import js from '@eslint/js';
import prettier from 'eslint-config-prettier';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from 'typescript-eslint';

const layering = (message, ...patterns) => ({
  'no-restricted-imports': ['error', { patterns: patterns.map((group) => ({ group, message })) }],
});

export default tseslint.config(
  { ignores: ['dist', 'coverage', 'src/api/**'] },
  js.configs.recommended,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  jsxA11y.flatConfigs.recommended,
  {
    languageOptions: {
      globals: globals.browser,
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    plugins: { 'react-hooks': reactHooks, 'react-refresh': reactRefresh },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    },
  },
  // Layering: page -> hook -> service -> generated client (see docs/02-architecture/frontend.md).
  {
    files: ['src/components/**', 'src/pages/**'],
    ignores: ['**/*.test.{ts,tsx}'],
    rules: layering('Components and pages must use hooks, not services or the generated client.', [
      '**/services/**',
      '**/api/**',
    ]),
  },
  {
    files: ['src/utils/**'],
    ignores: ['**/*.test.{ts,tsx}'],
    rules: layering('utils must stay pure: no React, services or hooks.', [
      'react',
      'react-dom',
      '**/services/**',
      '**/hooks/**',
      '**/components/**',
    ]),
  },
  {
    files: ['src/services/**'],
    rules: layering('services must not depend on React or UI code.', [
      'react',
      'react-dom',
      '**/hooks/**',
      '**/components/**',
      '**/pages/**',
    ]),
  },
  {
    files: ['**/*.js'],
    extends: [tseslint.configs.disableTypeChecked],
    languageOptions: { globals: globals.node },
  },
  prettier,
);
