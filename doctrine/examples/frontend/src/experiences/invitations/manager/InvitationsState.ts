import type { AppFailure } from "../../../common/failures/AppFailure";
import type { Invitation } from "../models/Invitation";
import type { TeamMember } from "../models/TeamMember";

// FE-STATE-4: who is signed in and what the screen has loaded change
// independently, so they are two unions with their own transitions.

export class SessionIdle {
  readonly kind = "SessionIdle" as const;
}

export class SessionChecking {
  readonly kind = "SessionChecking" as const;
}

export class SessionSignedOut {
  readonly kind = "SessionSignedOut" as const;
}

export class SessionAuthenticated {
  readonly kind = "SessionAuthenticated" as const;
  constructor(readonly user: TeamMember) {}
}

export class SessionFailed {
  readonly kind = "SessionFailed" as const;
  constructor(readonly failure: AppFailure) {}
}

export type SessionState = SessionIdle | SessionChecking | SessionSignedOut | SessionAuthenticated | SessionFailed;

/** FE-STATE-5: the background member search, held as a field of `FlowLoaded`. */
export interface DirectorySearch {
  readonly query: string;
  readonly status: "idle" | "searching" | "loaded";
  readonly members: readonly TeamMember[];
}

export const idleDirectory: DirectorySearch = { query: "", status: "idle", members: [] };

export class FlowIdle {
  readonly kind = "FlowIdle" as const;
}

/** FE-STATE-7: carries the key only, so a list loaded for another team cannot be shown under it. */
export class FlowLoading {
  readonly kind = "FlowLoading" as const;
  constructor(readonly teamId: string) {}
}

export class FlowLoaded {
  readonly kind = "FlowLoaded" as const;
  constructor(
    readonly teamId: string,
    readonly invitations: readonly Invitation[],
    readonly directory: DirectorySearch,
  ) {}

  /** A search changes only the sub-state; the loaded invitations are carried over. */
  withDirectory(directory: DirectorySearch): FlowLoaded {
    return new FlowLoaded(this.teamId, this.invitations, directory);
  }
}

/** FE-STATE-6: an invite or a revoke is in flight and owns the flow until it settles. */
export class FlowSubmitting {
  readonly kind = "FlowSubmitting" as const;
  constructor(
    readonly teamId: string,
    readonly invitations: readonly Invitation[],
  ) {}
}

/** Keeps the team and the last known list so the screen can offer a reload without going blank. */
export class FlowFailed {
  readonly kind = "FlowFailed" as const;
  constructor(
    readonly failure: AppFailure,
    readonly teamId: string,
    readonly invitations: readonly Invitation[],
  ) {}
}

export type FlowState = FlowIdle | FlowLoading | FlowLoaded | FlowSubmitting | FlowFailed;
