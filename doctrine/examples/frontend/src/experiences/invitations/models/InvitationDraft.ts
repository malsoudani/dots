import { Invitation } from "./Invitation";
import type { InvitationFlags } from "./InvitationFlags";
import { DEFAULT_ROLE } from "./Role";
import type { Role } from "./Role";

/** What the form reports on every change: raw input text, not yet validated (FE-MGR-5). */
export interface InvitationDraft {
  readonly email: string;
  readonly role: Role;
  readonly message: string;
  /** A calendar date as `YYYY-MM-DD`, or empty for no expiry. */
  readonly expiresOn: string;
}

export const emptyDraft: InvitationDraft = { email: "", role: DEFAULT_ROLE, message: "", expiresOn: "" };

/** What the service sends. Optional fields are absent, never empty (CT-3). */
export interface InvitationSubmission {
  readonly email: string;
  readonly role: Role;
  readonly message?: string;
  readonly expiresAt?: string;
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MESSAGE_MAX_LENGTH = 500;

function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

/** FE-MGR-4: with the flag off the expiry is neither validated nor sent. */
function activeExpiry(draft: InvitationDraft, flags: InvitationFlags): string {
  return flags.expiryEnabled ? draft.expiresOn : "";
}

function isCalendarDate(value: string): boolean {
  const parsed = new Date(`${value}T00:00:00Z`);
  // Date accepts 2030-02-31 and rolls it into March, so compare the round trip.
  return !Number.isNaN(parsed.getTime()) && parsed.toISOString().startsWith(value);
}

export function draftValid(draft: InvitationDraft, flags: InvitationFlags): boolean {
  const expiresOn = activeExpiry(draft, flags);
  return (
    EMAIL_PATTERN.test(normalizeEmail(draft.email)) &&
    draft.message.trim().length <= MESSAGE_MAX_LENGTH &&
    (expiresOn === "" || isCalendarDate(expiresOn))
  );
}

export function submissionFromDraft(draft: InvitationDraft, flags: InvitationFlags): InvitationSubmission {
  const message = draft.message.trim();
  const expiresOn = activeExpiry(draft, flags);
  return {
    email: normalizeEmail(draft.email),
    role: draft.role,
    ...(message === "" ? {} : { message }),
    // The API requires an offset; the invitation stays valid through the chosen day in UTC.
    ...(expiresOn === "" ? {} : { expiresAt: `${expiresOn}T23:59:59+00:00` }),
  };
}

/** Inviting an email that already has a pending invitation returns that invitation and changes nothing. */
export function isAlreadyInvited(email: string, invitations: readonly Invitation[]): boolean {
  const normalized = normalizeEmail(email);
  return invitations.some(
    (invitation) => Invitation.isPending(invitation) && normalizeEmail(invitation.email) === normalized,
  );
}
