import type { InvitationDraft } from "../models/InvitationDraft";

// FE-STATE-1: every intent that can enter the manager is a named type with a
// literal `kind`. Presentation constructs these and decides nothing else.

/** The screen opened and needs to know who is signed in. */
export class SessionRequested {
  readonly kind = "SessionRequested" as const;
}

/** The screen is showing this team, or the user asked to reload it. */
export class InvitationsRequested {
  readonly kind = "InvitationsRequested" as const;
  constructor(readonly teamId: string) {}
}

export class DirectorySearchRequested {
  readonly kind = "DirectorySearchRequested" as const;
  constructor(readonly query: string) {}
}

/** FE-MGR-5: the form reports its whole snapshot on every change. */
export class DraftChanged {
  readonly kind = "DraftChanged" as const;
  constructor(readonly draft: InvitationDraft) {}
}

export class SubmitRequested {
  readonly kind = "SubmitRequested" as const;
}

export class RevokeRequested {
  readonly kind = "RevokeRequested" as const;
  constructor(readonly invitationId: string) {}
}

export type InvitationsEvent =
  | SessionRequested
  | InvitationsRequested
  | DirectorySearchRequested
  | DraftChanged
  | SubmitRequested
  | RevokeRequested;
