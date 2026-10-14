import type { Role } from "./Role";

export type InvitationStatus = "pending" | "accepted" | "revoked";

export interface Invitation {
  readonly id: string;
  readonly teamId: string;
  readonly email: string;
  readonly role: Role;
  readonly status: InvitationStatus;
  readonly message: string;
  readonly expiresAt: string | null;
  readonly createdAt: string;
}

/** The wire shape of one invitation. These field names stop here (FE-SVC-7). */
export interface InvitationResponse {
  readonly id: string;
  readonly team_id: string;
  readonly email: string;
  readonly role: Role;
  readonly status: InvitationStatus;
  readonly message?: string | null;
  readonly expires_at?: string | null;
  readonly created_at: string;
}

export const Invitation = {
  /** CT-6: optional fields may be absent or null on older records; both get the same default. */
  fromResponse(raw: InvitationResponse): Invitation {
    return {
      id: raw.id,
      teamId: raw.team_id,
      email: raw.email,
      role: raw.role,
      status: raw.status,
      message: raw.message ?? "",
      expiresAt: raw.expires_at ?? null,
      createdAt: raw.created_at,
    };
  },

  /** Only a pending invitation can be revoked or blocks a new one for the same email. */
  isPending(invitation: Invitation): boolean {
    return invitation.status === "pending";
  },
};
