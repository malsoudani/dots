import { isLeft } from "fp-ts/Either";
import { describe, expect, it } from "vitest";
import { writeAuthTokens } from "../../../common/auth/AuthStorage";
import { ApiClient } from "../../../common/http/ApiClient";
import { FakeTransport } from "../../../common/testing/FakeTransport";
import { MemoryStorage } from "../../../common/testing/MemoryStorage";
import { SESSION_READ_FAILED } from "./ISessionService";
import { SessionApiService } from "./SessionApiService";

function setup() {
  const storage = new MemoryStorage();
  writeAuthTokens(storage, { access: "access-1", refresh: "refresh-1" });
  const transport = new FakeTransport();
  const apiClient = new ApiClient({ baseUrl: "https://api.example.com", storage, transport: transport.send });
  return { transport, service: new SessionApiService(apiClient) };
}

describe("SessionApiService", () => {
  it("reads the signed-in user with an authenticated GET", async () => {
    const { transport, service } = setup();
    transport.respondJson(200, {
      authenticated: true,
      user: { id: "user-1", email: "ana@example.com", name: "Ana Example" },
    });

    const result = await service.readSession();

    expect(result).toEqual({ _tag: "Right", right: { id: "user-1", email: "ana@example.com", name: "Ana Example" } });
    expect(transport.requests).toEqual([
      {
        url: "https://api.example.com/api/auth/session/",
        method: "GET",
        headers: { Accept: "application/json", Authorization: "Bearer access-1" },
      },
    ]);
  });

  it("returns SESSION_READ_FAILED with its fallback message when the body is not the session contract", async () => {
    const { transport, service } = setup();
    transport.respondJson(200, { unexpected: true });

    const result = await service.readSession();

    expect(isLeft(result) && result.left.code).toBe(SESSION_READ_FAILED);
    expect(isLeft(result) && result.left.message).toBe("Your session could not be checked. Try again.");
  });
});
