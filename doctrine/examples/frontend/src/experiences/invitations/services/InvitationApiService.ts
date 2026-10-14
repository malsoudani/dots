import { left, right } from "fp-ts/Either";
import type { Either } from "fp-ts/Either";
import type { AppFailure } from "../../../common/failures/AppFailure";
import { toAppFailure } from "../../../common/failures/toAppFailure";
import type { ApiClient, JsonRequest } from "../../../common/http/ApiClient";
import { Invitation } from "../models/Invitation";
import type { InvitationResponse } from "../models/Invitation";
import type { InvitationSubmission } from "../models/InvitationDraft";
import { TeamMember } from "../models/TeamMember";
import type { TeamMemberResponse } from "../models/TeamMember";
import {
  DIRECTORY_SEARCH_FAILED,
  INVITATION_REVOKE_FAILED,
  INVITATION_SUBMIT_FAILED,
  INVITATIONS_LOAD_FAILED,
} from "./IInvitationService";
import type { IInvitationService } from "./IInvitationService";

interface InvitationsResponse {
  readonly team_id: string;
  readonly invitations: readonly InvitationResponse[];
}

interface MembersResponse {
  readonly team_id: string;
  readonly members: readonly TeamMemberResponse[];
}

type InvitationsResult = Either<AppFailure, readonly Invitation[]>;

export class InvitationApiService implements IInvitationService {
  // FE-SVC-8: the in-flight guard is a field of this instance, never module state,
  // so it cannot leak between mounts or between tests.
  private readonly loadsInFlight = new Map<string, Promise<InvitationsResult>>();

  constructor(private readonly apiClient: ApiClient) {}

  loadInvitations(teamId: string): Promise<InvitationsResult> {
    const inFlight = this.loadsInFlight.get(teamId);
    if (inFlight !== undefined) {
      return inFlight;
    }
    const load = this.requestInvitations(
      "/api/invitations/",
      { query: { team_id: teamId } },
      INVITATIONS_LOAD_FAILED,
      "The invitations could not be loaded. Try again.",
    ).finally(() => this.loadsInFlight.delete(teamId));
    this.loadsInFlight.set(teamId, load);
    return load;
  }

  createInvitation(teamId: string, submission: InvitationSubmission): Promise<InvitationsResult> {
    const body = {
      team_id: teamId,
      email: submission.email,
      role: submission.role,
      // CT-3: an empty optional is omitted, never sent as null or "".
      ...(submission.message === undefined ? {} : { message: submission.message }),
      ...(submission.expiresAt === undefined ? {} : { expires_at: submission.expiresAt }),
    };
    return this.requestInvitations(
      "/api/invitations/",
      { method: "POST", body },
      INVITATION_SUBMIT_FAILED,
      "The invitation could not be sent. Try again.",
    );
  }

  revokeInvitation(invitationId: string): Promise<InvitationsResult> {
    return this.requestInvitations(
      `/api/invitations/${encodeURIComponent(invitationId)}/revoke/`,
      { method: "POST" },
      INVITATION_REVOKE_FAILED,
      "The invitation could not be revoked. Try again.",
    );
  }

  async searchDirectory(teamId: string, query: string): Promise<Either<AppFailure, readonly TeamMember[]>> {
    try {
      const raw = await this.apiClient.requestAuthenticatedJson<MembersResponse>(
        `/api/teams/${encodeURIComponent(teamId)}/members/`,
        { query: { q: query } },
      );
      return right(raw.members.map((member) => TeamMember.fromResponse(member)));
    } catch (error) {
      return left(toAppFailure(error, DIRECTORY_SEARCH_FAILED, "The team directory could not be searched. Try again."));
    }
  }

  /** Reads and writes answer with the same snapshot (CT-5), so one mapper serves all three. */
  private async requestInvitations(
    path: string,
    request: JsonRequest,
    code: string,
    fallbackMessage: string,
  ): Promise<InvitationsResult> {
    try {
      const raw = await this.apiClient.requestAuthenticatedJson<InvitationsResponse>(path, request);
      return right(raw.invitations.map((invitation) => Invitation.fromResponse(invitation)));
    } catch (error) {
      return left(toAppFailure(error, code, fallbackMessage));
    }
  }
}
