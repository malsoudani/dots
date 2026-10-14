import { HttpError } from "../http/HttpError";
import { AppFailure, SESSION_EXPIRED } from "./AppFailure";

/**
 * FE-SVC-3: only an HttpError carries text that is safe to show. Anything else
 * (a network failure, a parser error) is replaced by the service's fallback
 * message, and the original stays on `cause`.
 */
export function toAppFailure(error: unknown, code: string, fallbackMessage: string): AppFailure {
  if (!(error instanceof HttpError)) {
    return new AppFailure(code, fallbackMessage, error);
  }
  // CT-2: 401 means dead credentials and nothing else, whichever service saw it.
  return new AppFailure(error.status === 401 ? SESSION_EXPIRED : code, error.message, error);
}
