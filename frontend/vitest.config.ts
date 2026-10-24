import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['src/tests/setup.ts'],
    css: false,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'cobertura', 'html'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/api/**', // generated
        'src/main.tsx', // bootstrap only
        'src/vite-env.d.ts',
        'src/tests/**',
        'src/**/*.test.{ts,tsx}',
      ],
      thresholds: {
        lines: 80,
        branches: 80,
        functions: 80,
        statements: 80,
      },
    },
  },
});
