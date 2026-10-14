import { Invitation } from "../models/Invitation";
import { expirySummary, invitationsCopy, roleLabel, statusLabel } from "./invitationsCopy";

interface InvitationListProps {
  readonly invitations: readonly Invitation[];
  /** Passed only while the flow accepts a revoke; without it no button is rendered. */
  readonly onRevoke?: (invitationId: string) => void;
}

export function InvitationList({ invitations, onRevoke }: InvitationListProps) {
  if (invitations.length === 0) {
    return <p>{invitationsCopy.noInvitations}</p>;
  }
  return (
    <table>
      <tbody>
        {invitations.map((invitation) => (
          <tr key={invitation.id}>
            <td>{invitation.email}</td>
            <td>{roleLabel(invitation.role)}</td>
            <td>{statusLabel(invitation.status)}</td>
            <td>{expirySummary(invitation.expiresAt)}</td>
            <td>
              {onRevoke !== undefined && Invitation.isPending(invitation) && (
                // FE-UI-4: end-to-end tests select on this hook.
                <button type="button" data-testid="invitation-revoke" onClick={() => onRevoke(invitation.id)}>
                  {invitationsCopy.revoke}
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
