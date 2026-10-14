import { describe, expect, it } from "vitest";
import { AppFailure } from "../../../common/failures/AppFailure";
import type { Invitation } from "../models/Invitation";
import { emptyDraft } from "../models/InvitationDraft";
import type { InvitationDraft } from "../models/InvitationDraft";
import {
  FlowFailed,
  FlowIdle,
  FlowLoaded,
  FlowLoading,
  FlowSubmitting,
  SessionAuthenticated,
  SessionChecking,
  SessionSignedOut,
  idleDirectory,
} from "./InvitationsState";
import { deriveView } from "./InvitationsView";
import type { ViewInputs } from "./InvitationsView";

function invitation(id: string, email: string, status: Invitation["status"]): Invitation {
  return {
    id,
    teamId: "team-1",
    email,
    role: "member",
    status,
    message: "",
    expiresAt: null,
    createdAt: "2030-01-01T09:00:00+00:00",
  };
}

const invitations = [
  invitation("inv-1", "ana@example.com", "pending"),
  invitation("inv-2", "ben@example.com", "pending"),
  invitation("inv-3", "cy@example.com", "revoked"),
];
const validDraft: InvitationDraft = { ...emptyDraft, email: "dee@example.com" };

function inputs(overrides: Partial<ViewInputs> = {}): ViewInputs {
  return {
    sessionState: new SessionAuthenticated({ id: "user-1", email: "owner@example.com", name: "Owner" }),
    flowState: new FlowLoaded("team-1", invitations, idleDirectory),
    draft: validDraft,
    flags: { expiryEnabled: false },
    ...overrides,
  };
}

describe("deriveView", () => {
  it("allows submitting when authenticated and loaded with a valid draft for a new email", () => {
    expect(deriveView(inputs()).canSubmit).toBe(true);
  });

  it("forbids submitting when signed out, checking, not loaded, invalid or already invited", () => {
    const blocked = [
      inputs({ sessionState: new SessionSignedOut() }),
      inputs({ sessionState: new SessionChecking() }),
      inputs({ flowState: new FlowLoading("team-1") }),
      inputs({ flowState: new FlowSubmitting("team-1", invitations) }),
      inputs({ flowState: new FlowFailed(new AppFailure("ANY", "Try again."), "team-1", invitations) }),
      inputs({ draft: { ...validDraft, email: "dee@" } }),
      inputs({ draft: { ...validDraft, email: "Ana@example.com" } }),
    ];

    expect(blocked.map((input) => deriveView(input).canSubmit)).toEqual(blocked.map(() => false));
  });

  it("counts only pending invitations and counts none while idle or loading", () => {
    expect(deriveView(inputs()).pendingCount).toBe(2);
    expect(deriveView(inputs({ flowState: new FlowSubmitting("team-1", invitations) })).pendingCount).toBe(2);
    expect(deriveView(inputs({ flowState: new FlowIdle() })).pendingCount).toBe(0);
    expect(deriveView(inputs({ flowState: new FlowLoading("team-1") })).pendingCount).toBe(0);
  });

  it("shows the expiry field and the invite-with-expiry intent only when the flag is on", () => {
    const dated: InvitationDraft = { ...validDraft, expiresOn: "2030-01-31" };
    const on = { expiryEnabled: true };
    const off = { expiryEnabled: false };

    expect(deriveView(inputs({ flags: on, draft: dated }))).toMatchObject({
      showExpiryField: true,
      submitIntent: "invite-with-expiry",
    });
    expect(deriveView(inputs({ flags: on }))).toMatchObject({ showExpiryField: true, submitIntent: "invite" });
    expect(deriveView(inputs({ flags: off, draft: dated }))).toMatchObject({
      showExpiryField: false,
      submitIntent: "invite",
    });
  });
});
