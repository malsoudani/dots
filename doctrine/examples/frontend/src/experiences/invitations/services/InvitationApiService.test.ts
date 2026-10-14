import { isLeft, isRight } from "fp-ts/Either";
import type { Either } from "fp-ts/Either";
import { describe, expect, it } from "vitest";
import { writeAuthTokens } from "../../../common/auth/AuthStorage";
import { SESSION_EXPIRED } from "../../../common/failures/AppFailure";
import type { AppFailure } from "../../../common/failures/AppFailure";
import { ApiClient } from "../../../common/http/ApiClient";
import { FakeTransport } from "../../../common/testing/FakeTransport";
import { MemoryStorage } from "../../../common/testing/MemoryStorage";
import {
  DIRECTORY_SEARCH_FAILED,
  INVITATION_REVOKE_FAILED,
  INVITATION_SUBMIT_FAILED,
  INVITATIONS_LOAD_FAILED,
} from "./IInvitationService";
import { InvitationApiService } from "./InvitationApiService";

const AUTHENTICATED = { Accept: "application/json", Authorization: "Bearer access-1" };
const AUTHENTICATED_JSON = { ...AUTHENTICATED, "Content-Type": "application/json" };

const wireInvitation = {
  id: "inv-1",
  team_id: "team-1",
  email: "ana@example.com",
  role: "member",
  status: "pending",
  message: "",
  expires_at: null,
  created_at: "2030-01-01T09:00:00+00:00",
};
const snapshot = { team_id: "team-1", invitations: [wireInvitation] };
const invitation = {
  id: "inv-1",
  teamId: "team-1",
  email: "ana@example.com",
  role: "member",
  status: "pending",
  message: "",
  expiresAt: null,
  createdAt: "2030-01-01T09:00:00+00:00",
};

function setup({ signedIn = true } = {}) {
  const storage = new MemoryStorage();
  if (signedIn) {
    writeAuthTokens(storage, { access: "access-1", refresh: "refresh-1" });
  }
  const transport = new FakeTransport();
  const apiClient = new ApiClient({ baseUrl: "https://api.example.com", storage, transport: transport.send });
  return { transport, service: new InvitationApiService(apiClient) };
}

function failureOf(result: Either<AppFailure, unknown>): AppFailure {
  if (!isLeft(result)) {
    throw new Error("expected a failure on the left");
  }
  return result.left;
}

function valueOf<T>(result: Either<AppFailure, T>): T {
  if (!isRight(result)) {
    throw new Error(`expected a success on the right, got ${result.left.code}`);
  }
  return result.right;
}

describe("InvitationApiService", () => {
  it("loads a team's invitations with an authenticated GET and returns models", async () => {
    const { transport, service } = setup();
    transport.respondJson(200, snapshot);

    const result = await service.loadInvitations("team-1");

    expect(valueOf(result)).toEqual([invitation]);
    expect(transport.requests).toEqual([
      { url: "https://api.example.com/api/invitations/?team_id=team-1", method: "GET", headers: AUTHENTICATED },
    ]);
  });

  it("reports each failed operation under its own code with the message the API wrote", async () => {
    const { transport, service } = setup();
    const submission = { email: "ana@example.com", role: "member" } as const;
    const operations = [
      [INVITATIONS_LOAD_FAILED, () => service.loadInvitations("team-9")],
      [INVITATION_SUBMIT_FAILED, () => service.createInvitation("team-9", submission)],
      [INVITATION_REVOKE_FAILED, () => service.revokeInvitation("inv-9")],
      [DIRECTORY_SEARCH_FAILED, () => service.searchDirectory("team-9", "ana")],
    ] as const;

    for (const [code, run] of operations) {
      transport.respondJson(404, { error: "Team team-9 was not found." });

      const failure = failureOf(await run());

      expect(failure.code).toBe(code);
      expect(failure.message).toBe("Team team-9 was not found.");
    }
  });

  it("replaces a network error with its fallback message and keeps the error on cause", async () => {
    const { transport, service } = setup();
    const networkError = new TypeError("Failed to fetch");
    transport.failNext(networkError);

    const failure = failureOf(await service.loadInvitations("team-1"));

    expect(failure.code).toBe(INVITATIONS_LOAD_FAILED);
    expect(failure.message).toBe("The invitations could not be loaded. Try again.");
    expect(failure.cause).toBe(networkError);
  });

  it("returns SESSION_EXPIRED without a request when no access token is stored", async () => {
    const { transport, service } = setup({ signedIn: false });

    const failure = failureOf(await service.loadInvitations("team-1"));

    expect(failure.code).toBe(SESSION_EXPIRED);
    expect(transport.requests).toEqual([]);
  });

  it("sends one request for two concurrent loads of the same team and a new one after it settles", async () => {
    const { transport, service } = setup();
    transport.respondJson(200, snapshot);

    const [first, second] = await Promise.all([service.loadInvitations("team-1"), service.loadInvitations("team-1")]);

    expect(valueOf(first)).toEqual([invitation]);
    expect(valueOf(second)).toEqual([invitation]);
    expect(transport.requests).toHaveLength(1);

    transport.respondJson(200, { team_id: "team-1", invitations: [] });

    expect(valueOf(await service.loadInvitations("team-1"))).toEqual([]);
    expect(transport.requests).toHaveLength(2);
  });

  it("creates an invitation with a snake_case body and sends message and expires_at only when present", async () => {
    const { transport, service } = setup();
    transport.respondJson(200, snapshot);
    transport.respondJson(200, snapshot);

    const result = await service.createInvitation("team-1", { email: "ana@example.com", role: "member" });
    await service.createInvitation("team-1", {
      email: "ben@example.com",
      role: "admin",
      message: "Welcome aboard",
      expiresAt: "2030-01-31T23:59:59+00:00",
    });

    expect(valueOf(result)).toEqual([invitation]);
    expect(transport.requests).toEqual([
      {
        url: "https://api.example.com/api/invitations/",
        method: "POST",
        headers: AUTHENTICATED_JSON,
        body: JSON.stringify({ team_id: "team-1", email: "ana@example.com", role: "member" }),
      },
      {
        url: "https://api.example.com/api/invitations/",
        method: "POST",
        headers: AUTHENTICATED_JSON,
        body: JSON.stringify({
          team_id: "team-1",
          email: "ben@example.com",
          role: "admin",
          message: "Welcome aboard",
          expires_at: "2030-01-31T23:59:59+00:00",
        }),
      },
    ]);
  });

  it("revokes with a POST to the invitation's revoke path and returns the updated snapshot", async () => {
    const { transport, service } = setup();
    transport.respondJson(200, { team_id: "team-1", invitations: [{ ...wireInvitation, status: "revoked" }] });

    const result = await service.revokeInvitation("inv-1");

    expect(valueOf(result)).toEqual([{ ...invitation, status: "revoked" }]);
    expect(transport.requests).toEqual([
      { url: "https://api.example.com/api/invitations/inv-1/revoke/", method: "POST", headers: AUTHENTICATED },
    ]);
  });

  it("searches the team directory with the query and returns members", async () => {
    const { transport, service } = setup();
    transport.respondJson(200, {
      team_id: "team-1",
      members: [{ id: "user-2", email: "ben@example.com", name: "Ben" }],
    });

    const result = await service.searchDirectory("team-1", "be n");

    expect(valueOf(result)).toEqual([{ id: "user-2", email: "ben@example.com", name: "Ben" }]);
    expect(transport.requests).toEqual([
      { url: "https://api.example.com/api/teams/team-1/members/?q=be+n", method: "GET", headers: AUTHENTICATED },
    ]);
  });
});
