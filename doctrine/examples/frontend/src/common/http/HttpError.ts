/**
 * CT-1: the one error type the HTTP client throws. `message` is either the text of
 * the API error contract or the client's own status-based sentence, never a
 * browser or parser string.
 */
export class HttpError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "HttpError";
  }
}
