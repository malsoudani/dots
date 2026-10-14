import { describe, expect, it } from "vitest";
import { Invitation } from "./Invitation";
import { draftValid, emptyDraft, isAlreadyInvited, submissionFromDraft } from "./InvitationDraft";
import type { InvitationDraft } from "./InvitationDraft";

const expiryOn = { expiryEnabled: true };
const expiryOff = { expiryEnabled: false };

function draft(overrides: Partial<InvitationDraft> = {}): InvitationDraft {
  return { ...emptyDraft, email: "ana@example.com", ...overrides };
}

function invitation(email: string, status: Invitation["status"]): Invitation {
  return Invitation.fromResponse({
    id: `inv-${email}`,
    team_id: "team-1",
    email,
    role: "member",
    status,
    created_at: "2030-01-01T09:00:00+00:00",
  });
}

describe("draftValid", () => {
  it("accepts a well-formed email and rejects a blank or malformed one", () => {
    expect(draftValid(draft(), expiryOff)).toBe(true);
    for (const email of ["", "   ", "ana", "ana@", "ana@example", "ana smith@example.com"]) {
      expect(draftValid(draft({ email }), expiryOff), email).toBe(false);
    }
  });

  it("accepts a 500-character message and rejects a 501-character one", () => {
    expect(draftValid(draft({ message: "m".repeat(500) }), expiryOff)).toBe(true);
    expect(draftValid(draft({ message: "m".repeat(501) }), expiryOff)).toBe(false);
  });

  it("requires the expiry to be a calendar date when expiry is enabled and ignores it when disabled", () => {
    expect(draftValid(draft({ expiresOn: "2030-01-31" }), expiryOn)).toBe(true);
    expect(draftValid(draft({ expiresOn: "2030-02-31" }), expiryOn)).toBe(false);
    expect(draftValid(draft({ expiresOn: "next week" }), expiryOn)).toBe(false);
    expect(draftValid(draft({ expiresOn: "next week" }), expiryOff)).toBe(true);
  });
});

describe("submissionFromDraft", () => {
  it("normalizes the email and omits an empty message and an empty expiry", () => {
    const submission = submissionFromDraft(draft({ email: "  Ana@Example.com ", message: "   " }), expiryOn);

    expect(submission).toEqual({ email: "ana@example.com", role: "member" });
  });

  it("sends the trimmed message, the role and the expiry as the end of that day with an offset", () => {
    const submission = submissionFromDraft(
      draft({ role: "admin", message: " Welcome aboard ", expiresOn: "2030-01-31" }),
      expiryOn,
    );

    expect(submission).toEqual({
      email: "ana@example.com",
      role: "admin",
      message: "Welcome aboard",
      expiresAt: "2030-01-31T23:59:59+00:00",
    });
  });

  it("omits the expiry when expiry is disabled even if the draft carries one", () => {
    const submission = submissionFromDraft(draft({ expiresOn: "2030-01-31" }), expiryOff);

    expect(submission).toEqual({ email: "ana@example.com", role: "member" });
  });
});

describe("isAlreadyInvited", () => {
  it("is true only when a pending invitation has the same email, ignoring case and surrounding spaces", () => {
    const invitations = [invitation("ana@example.com", "pending"), invitation("ben@example.com", "revoked")];

    expect(isAlreadyInvited(" Ana@Example.com ", invitations)).toBe(true);
    expect(isAlreadyInvited("ben@example.com", invitations)).toBe(false);
    expect(isAlreadyInvited("cy@example.com", invitations)).toBe(false);
  });
});
