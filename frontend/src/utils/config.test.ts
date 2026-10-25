import { describe, expect, it, vi } from 'vitest';

import { ConfigError, getConfig, loadConfig, setConfig } from './config';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status });
}

describe('loadConfig', () => {
  it('loads and stores a valid config', async () => {
    const fetcher = vi.fn().mockResolvedValue(jsonResponse({ apiBaseUrl: '', env: 'dev' }));
    const config = await loadConfig(fetcher);
    expect(config).toEqual({ apiBaseUrl: '', env: 'dev' });
    expect(getConfig()).toEqual(config);
    expect(fetcher).toHaveBeenCalledWith('/config.json', { cache: 'no-store' });
  });

  it('fails with a ConfigError when the file is missing', async () => {
    const fetcher = vi.fn().mockResolvedValue(jsonResponse({}, 404));
    await expect(loadConfig(fetcher)).rejects.toThrow(/HTTP 404/);
  });

  it('rejects a config with missing keys', async () => {
    const fetcher = vi.fn().mockResolvedValue(jsonResponse({ env: 'dev' }));
    await expect(loadConfig(fetcher)).rejects.toBeInstanceOf(ConfigError);
  });

  it('rejects non-object JSON', async () => {
    const fetcher = vi.fn().mockResolvedValue(jsonResponse('nope'));
    await expect(loadConfig(fetcher)).rejects.toBeInstanceOf(ConfigError);
  });
});

describe('getConfig', () => {
  it('returns what setConfig stored', () => {
    setConfig({ apiBaseUrl: 'https://api.example.com', env: 'prod' });
    expect(getConfig().apiBaseUrl).toBe('https://api.example.com');
  });
});
