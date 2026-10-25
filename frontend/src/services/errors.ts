import { UserFacingError } from '../utils/errors';

/** Error raised for non-2xx API responses, built from the backend error envelope. */
export class ApiError extends UserFacingError {
  override name = 'ApiError';

  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
    readonly requestId?: string,
  ) {
    super(message);
  }
}

interface Envelope {
  error: { code?: unknown; message?: unknown; request_id?: unknown };
}

function isEnvelope(value: unknown): value is Envelope {
  return (
    typeof value === 'object' &&
    value !== null &&
    'error' in value &&
    typeof value.error === 'object' &&
    value.error !== null
  );
}

/** Build an {@link ApiError} from a status code and the parsed response body. */
export function toApiError(status: number, body: unknown): ApiError {
  if (!isEnvelope(body)) {
    return new ApiError(`Request failed (HTTP ${String(status)})`, status, 'unknown');
  }
  const { code, message, request_id: requestId } = body.error;
  return new ApiError(
    typeof message === 'string' ? message : `Request failed (HTTP ${String(status)})`,
    status,
    typeof code === 'string' ? code : 'unknown',
    typeof requestId === 'string' ? requestId : undefined,
  );
}
