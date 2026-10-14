/** Shared by every service: the manager signs the user out on this code (FE-SVC-2). */
export const SESSION_EXPIRED = "SESSION_EXPIRED";

/**
 * FE-SVC-2: the single failure shape that leaves a service. `code` is what managers
 * branch on, `message` is safe to render, `cause` is for logs and is never rendered.
 */
export class AppFailure {
  constructor(
    readonly code: string,
    readonly message: string,
    readonly cause?: unknown,
  ) {}
}
