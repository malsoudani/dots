import { Invitation } from "../models/Invitation";
import { draftValid, isAlreadyInvited, submissionFromDraft } from "../models/InvitationDraft";
import type { InvitationDraft } from "../models/InvitationDraft";
import type { InvitationFlags } from "../models/InvitationFlags";
import type { FlowState, SessionState } from "./InvitationsState";

/** FE-STATE-8: an intent, not a label. Presentation turns it into words. */
export type SubmitIntent = "invite" | "invite-with-expiry";

export interface InvitationsView {
  readonly canSubmit: boolean;
  readonly showExpiryField: boolean;
  readonly pendingCount: number;
  readonly submitIntent: SubmitIntent;
}

export interface ViewInputs {
  readonly sessionState: SessionState;
  readonly flowState: FlowState;
  readonly draft: InvitationDraft;
  readonly flags: InvitationFlags;
}

function shownInvitations(flowState: FlowState): readonly Invitation[] {
  switch (flowState.kind) {
    case "FlowIdle":
    case "FlowLoading":
      return [];
    case "FlowLoaded":
    case "FlowSubmitting":
    case "FlowFailed":
      return flowState.invitations;
  }
}

/**
 * FE-STATE-9: everything the screen computes from state is computed here, once.
 * The manager uses the same `canSubmit` to guard `SubmitRequested`.
 */
export function deriveView({ sessionState, flowState, draft, flags }: ViewInputs): InvitationsView {
  return {
    canSubmit:
      sessionState.kind === "SessionAuthenticated" &&
      flowState.kind === "FlowLoaded" &&
      draftValid(draft, flags) &&
      !isAlreadyInvited(draft.email, flowState.invitations),
    showExpiryField: flags.expiryEnabled,
    pendingCount: shownInvitations(flowState).filter(Invitation.isPending).length,
    submitIntent: submissionFromDraft(draft, flags).expiresAt === undefined ? "invite" : "invite-with-expiry",
  };
}
