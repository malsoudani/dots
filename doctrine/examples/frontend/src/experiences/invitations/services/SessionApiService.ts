import { left, right } from "fp-ts/Either";
import type { Either } from "fp-ts/Either";
import type { AppFailure } from "../../../common/failures/AppFailure";
import { toAppFailure } from "../../../common/failures/toAppFailure";
import type { ApiClient } from "../../../common/http/ApiClient";
import { TeamMember } from "../models/TeamMember";
import type { TeamMemberResponse } from "../models/TeamMember";
import { SESSION_READ_FAILED } from "./ISessionService";
import type { ISessionService } from "./ISessionService";

interface SessionResponse {
  readonly authenticated: boolean;
  readonly user: TeamMemberResponse;
}

export class SessionApiService implements ISessionService {
  constructor(private readonly apiClient: ApiClient) {}

  async readSession(): Promise<Either<AppFailure, TeamMember>> {
    try {
      const raw = await this.apiClient.requestAuthenticatedJson<SessionResponse>("/api/auth/session/");
      return right(TeamMember.fromResponse(raw.user));
    } catch (error) {
      return left(toAppFailure(error, SESSION_READ_FAILED, "Your session could not be checked. Try again."));
    }
  }
}
