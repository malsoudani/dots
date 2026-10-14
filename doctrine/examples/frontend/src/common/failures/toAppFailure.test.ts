import { describe, expect, it } from "vitest";
import { HttpError } from "../http/HttpError";
import { SESSION_EXPIRED } from "./AppFailure";
import { toAppFailure } from "./toAppFailure";

describe("toAppFailure", () => {
  it("passes an HttpError message through under the service code and keeps the error on cause", () => {
    const error = new HttpError(400, "Enter a valid email address");

    const failure = toAppFailure(error, "INVITATION_SUBMIT_FAILED", "The invitation could not be sent.");

    expect(failure.code).toBe("INVITATION_SUBMIT_FAILED");
    expect(failure.message).toBe("Enter a valid email address");
    expect(failure.cause).toBe(error);
  });

  it("replaces a non-HTTP error message with the fallback and keeps the original on cause", () => {
    const error = new TypeError("Failed to fetch");

    const failure = toAppFailure(error, "INVITATIONS_LOAD_FAILED", "Invitations could not be loaded.");

    expect(failure.code).toBe("INVITATIONS_LOAD_FAILED");
    expect(failure.message).toBe("Invitations could not be loaded.");
    expect(failure.cause).toBe(error);
  });

  it("maps a 401 HttpError to the shared session-expired code", () => {
    const error = new HttpError(401, "Your session has expired. Sign in again.");

    const failure = toAppFailure(error, "INVITATIONS_LOAD_FAILED", "Invitations could not be loaded.");

    expect(failure.code).toBe(SESSION_EXPIRED);
    expect(failure.message).toBe("Your session has expired. Sign in again.");
  });
});
