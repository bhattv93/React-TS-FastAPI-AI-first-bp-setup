import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { ConfigErrorScreen } from './ConfigErrorScreen';

describe('ConfigErrorScreen', () => {
  it('explains why the app could not start', () => {
    render(<ConfigErrorScreen message="config.json could not be loaded (HTTP 404)" />);
    expect(screen.getByRole('alert')).toHaveTextContent('The application could not start.');
    expect(screen.getByRole('alert')).toHaveTextContent('HTTP 404');
  });
});
