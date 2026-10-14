import type { Either } from "fp-ts/Either";
import type { AppFailure } from "../../../common/failures/AppFailure";
import type { Invitation } from "../models/Invitation";
import type { InvitationSubmission } from "../models/InvitationDraft";
import type { TeamMember } from "../models/TeamMember";

export const INVITATIONS_LOAD_FAILED = "INVITATIONS_LOAD_FAILED";
export const INVITATION_SUBMIT_FAILED = "INVITATION_SUBMIT_FAILED";
export const INVITATION_REVOKE_FAILED = "INVITATION_REVOKE_FAILED";
export const DIRECTORY_SEARCH_FAILED = "DIRECTORY_SEARCH_FAILED";

/**
 * FE-SVC-1: every method resolves to a result value, failure on the left. The
 * manager depends on this interface, so its tests run against a fake.
 * Both writes return the team's full updated list (CT-5).
 */
export interface IInvitationService {
  loadInvitations(teamId: string): Promise<Either<AppFailure, readonly Invitation[]>>;
  createInvitation(
    teamId: string,
    submission: InvitationSubmission,
  ): Promise<Either<AppFailure, readonly Invitation[]>>;
  revokeInvitation(invitationId: string): Promise<Either<AppFailure, readonly Invitation[]>>;
  searchDirectory(teamId: string, query: string): Promise<Either<AppFailure, readonly TeamMember[]>>;
}
