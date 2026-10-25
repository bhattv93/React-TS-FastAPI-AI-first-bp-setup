/** An error whose message was written for end users and is safe to display as is. */
export class UserFacingError extends Error {
  override name = 'UserFacingError';
}

const FALLBACK_MESSAGE = 'Something went wrong';

/**
 * Turn any thrown value into text that is safe to show to a user.
 *
 * Only {@link UserFacingError}s expose their message. Anything else (network failures, parse
 * errors, bugs) may carry internals, so it gets a generic message; the details belong in logs.
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof UserFacingError) {
    const requestId = (error as { requestId?: unknown }).requestId;
    return typeof requestId === 'string' ? `${error.message} (ref ${requestId})` : error.message;
  }
  return FALLBACK_MESSAGE;
}
