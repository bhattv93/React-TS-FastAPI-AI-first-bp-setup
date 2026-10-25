import { describe, expect, it } from 'vitest';

import { setConfig } from '../utils/config';
import { getApiClient } from './client';

describe('getApiClient', () => {
  it('reuses one client while the API base URL is unchanged', () => {
    setConfig({ apiBaseUrl: 'http://api.one', env: 'test' });
    expect(getApiClient()).toBe(getApiClient());
  });

  it('builds a new client when the API base URL changes', () => {
    setConfig({ apiBaseUrl: 'http://api.one', env: 'test' });
    const first = getApiClient();
    setConfig({ apiBaseUrl: 'http://api.two', env: 'test' });
    expect(getApiClient()).not.toBe(first);
  });
});
