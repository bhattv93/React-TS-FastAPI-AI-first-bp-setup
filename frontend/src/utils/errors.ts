/** Turn any thrown value into a message that is safe to show to a user. */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    const requestId = (error as { requestId?: unknown }).requestId;
    return typeof requestId === 'string' ? `${error.message} (ref ${requestId})` : error.message;
  }
  return 'Something went wrong';
}
