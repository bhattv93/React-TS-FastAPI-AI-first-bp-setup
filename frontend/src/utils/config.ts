import { UserFacingError } from './errors';

/** Runtime configuration loaded from `/config.json` (see docs/06-delivery/aws-frontend.md). */
export interface AppConfig {
  /** Origin of the API. Empty string means same-origin (CloudFront or the Vite proxy). */
  apiBaseUrl: string;
  env: string;
}

export class ConfigError extends UserFacingError {
  override name = 'ConfigError';
}

let current: AppConfig | undefined;

function isAppConfig(value: unknown): value is AppConfig {
  if (typeof value !== 'object' || value === null) return false;
  const candidate = value as Record<string, unknown>;
  return typeof candidate.apiBaseUrl === 'string' && typeof candidate.env === 'string';
}

/** Fetch and validate `/config.json`. Must complete before the app renders. */
export async function loadConfig(fetcher: typeof fetch = fetch): Promise<AppConfig> {
  const response = await fetcher('/config.json', { cache: 'no-store' });
  if (!response.ok) {
    throw new ConfigError(`config.json could not be loaded (HTTP ${String(response.status)})`);
  }
  const raw: unknown = await response.json();
  if (!isAppConfig(raw)) {
    throw new ConfigError('config.json is missing "apiBaseUrl" or "env"');
  }
  current = raw;
  return raw;
}

/** Set the configuration directly (used by tests). */
export function setConfig(config: AppConfig): void {
  current = config;
}

/** Return the loaded configuration or fail loudly if it has not been loaded. */
export function getConfig(): AppConfig {
  if (current === undefined) {
    throw new ConfigError('Configuration has not been loaded');
  }
  return current;
}
