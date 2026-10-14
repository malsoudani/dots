import type { Either } from "fp-ts/Either";
import type { AppFailure } from "../../../common/failures/AppFailure";
import type { TeamMember } from "../models/TeamMember";

export const SESSION_READ_FAILED = "SESSION_READ_FAILED";

export interface ISessionService {
  /** Resolves to the signed-in user, or to `SESSION_EXPIRED` on the left when nobody is signed in. */
  readSession(): Promise<Either<AppFailure, TeamMember>>;
}
