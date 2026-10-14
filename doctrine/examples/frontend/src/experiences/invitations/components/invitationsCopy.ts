import type { SubmitIntent } from "../manager/InvitationsView";
import type { InvitationStatus } from "../models/Invitation";
import type { Role } from "../models/Role";

// FE-STATE-8: every word this experience shows that the API did not write lives
// here. States carry intents and data; these functions turn them into text.

export const invitationsCopy = {
  title: "Team invitations",
  checkingSession: "Checking your session...",
  signedOut: "You are signed out. Sign in to manage invitations.",
  loading: "Loading invitations...",
  saving: "Saving...",
  retry: "Try again",
  email: "Email",
  role: "Role",
  message: "Message (optional)",
  expiresOn: "Expires on (optional)",
  directory: "Search current members",
  searching: "Searching...",
  noMembers: "No members match.",
  noInvitations: "No invitations yet.",
  revoke: "Revoke",
} as const;

const SUBMIT_LABELS: Record<SubmitIntent, string> = {
  invite: "Send invitation",
  "invite-with-expiry": "Send invitation with expiry",
};

const ROLE_LABELS: Record<Role, string> = { member: "Member", admin: "Admin" };

const STATUS_LABELS: Record<InvitationStatus, string> = {
  pending: "Pending",
  accepted: "Accepted",
  revoked: "Revoked",
};

export function submitLabel(intent: SubmitIntent): string {
  return SUBMIT_LABELS[intent];
}

export function roleLabel(role: Role): string {
  return ROLE_LABELS[role];
}

export function statusLabel(status: InvitationStatus): string {
  return STATUS_LABELS[status];
}

export function pendingSummary(count: number): string {
  if (count === 0) {
    return "No pending invitations";
  }
  return count === 1 ? "1 pending invitation" : `${count} pending invitations`;
}

export function expirySummary(expiresAt: string | null): string {
  return expiresAt === null ? "No expiry" : `Expires ${expiresAt.slice(0, 10)}`;
}
