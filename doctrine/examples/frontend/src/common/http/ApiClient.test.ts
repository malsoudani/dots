import { describe, expect, it } from "vitest";
import { readAccessToken, readRefreshToken, writeAccessToken, writeAuthTokens } from "../auth/AuthStorage";
import { FakeTransport } from "../testing/FakeTransport";
import { MemoryStorage } from "../testing/MemoryStorage";
import { ApiClient } from "./ApiClient";
import { HttpError } from "./HttpError";

function setup(tokens: { access: string; refresh: string } | null = { access: "access-1", refresh: "refresh-1" }) {
  const storage = new MemoryStorage();
  if (tokens !== null) {
    writeAuthTokens(storage, tokens);
  }
  const transport = new FakeTransport();
  const apiClient = new ApiClient({ baseUrl: "https://api.example.com", storage, transport: transport.send });
  return { storage, transport, apiClient };
}

async function thrownBy(request: Promise<unknown>): Promise<unknown> {
  return request.then(
    () => {
      throw new Error("expected the request to fail");
    },
    (error: unknown) => error,
  );
}

describe("ApiClient.requestJson", () => {
  it("builds the URL from base, path and query and sends no Authorization header", async () => {
    const { transport, apiClient } = setup();
    transport.respondJson(200, { status: "ok" });

    const body = await apiClient.requestJson("/api/status/", { query: { verbose: "1" } });

    expect(body).toEqual({ status: "ok" });
    expect(transport.requests).toEqual([
      { url: "https://api.example.com/api/status/?verbose=1", method: "GET", headers: { Accept: "application/json" } },
    ]);
  });

  it("throws an HttpError with the API's message, or a status-based one when the body is not the error contract", async () => {
    const { transport, apiClient } = setup();
    transport.respondJson(400, { error: "Enter a valid email address" });
    transport.respondText(502, "<html>Bad Gateway</html>");

    const contract = await thrownBy(apiClient.requestJson("/api/invitations/", { method: "POST", body: {} }));
    const other = await thrownBy(apiClient.requestJson("/api/status/"));

    expect(contract).toBeInstanceOf(HttpError);
    expect(contract).toMatchObject({ status: 400, message: "Enter a valid email address" });
    expect(other).toBeInstanceOf(HttpError);
    expect(other).toMatchObject({ status: 502, message: "The request failed (HTTP 502)." });
  });

  it("throws an HttpError when a 2xx body is not JSON", async () => {
    const { transport, apiClient } = setup();
    transport.respondText(200, "<html>Signed in elsewhere</html>");

    const error = await thrownBy(apiClient.requestJson("/api/status/"));

    expect(error).toBeInstanceOf(HttpError);
    expect(error).toMatchObject({ status: 200, message: "The server sent an unexpected response." });
  });
});

describe("ApiClient.requestAuthenticatedJson", () => {
  it("throws session-expired without a request when there is no access token", async () => {
    const { transport, apiClient } = setup(null);

    const error = await thrownBy(apiClient.requestAuthenticatedJson("/api/auth/session/"));

    expect(error).toBeInstanceOf(HttpError);
    expect(error).toMatchObject({ status: 401 });
    expect(transport.requests).toEqual([]);
  });

  it("refreshes once on 401, stores the new access token and retries with it", async () => {
    const { storage, transport, apiClient } = setup();
    transport.respondJson(401, { error: "Token expired." });
    transport.respondJson(200, { access: "access-2" });
    transport.respondJson(200, { team_id: "team-1" });

    const body = await apiClient.requestAuthenticatedJson("/api/invitations/", { query: { team_id: "team-1" } });

    expect(body).toEqual({ team_id: "team-1" });
    expect(transport.requests).toHaveLength(3);
    expect(transport.requests[0]).toEqual({
      url: "https://api.example.com/api/invitations/?team_id=team-1",
      method: "GET",
      headers: { Accept: "application/json", Authorization: "Bearer access-1" },
    });
    expect(transport.requests[1]).toEqual({
      url: "https://api.example.com/api/auth/token/refresh/",
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: "refresh-1" }),
    });
    expect(transport.requests[2]?.headers).toEqual({ Accept: "application/json", Authorization: "Bearer access-2" });
    expect(readAccessToken(storage)).toBe("access-2");
    expect(readRefreshToken(storage)).toBe("refresh-1");
  });

  it.each([401, 403])("clears both tokens and throws session-expired when the refresh answers %i", async (status) => {
    const { storage, transport, apiClient } = setup();
    transport.respondJson(401, { error: "Token expired." });
    transport.respondJson(status, { error: "Refresh token rejected." });

    const error = await thrownBy(apiClient.requestAuthenticatedJson("/api/invitations/"));

    expect(error).toMatchObject({ status: 401 });
    expect(readAccessToken(storage)).toBeNull();
    expect(readRefreshToken(storage)).toBeNull();
  });

  it("keeps both tokens and rethrows when the refresh fails with 503", async () => {
    const { storage, transport, apiClient } = setup();
    transport.respondJson(401, { error: "Token expired." });
    transport.respondJson(503, { error: "Try again shortly." });

    const error = await thrownBy(apiClient.requestAuthenticatedJson("/api/invitations/"));

    expect(error).toMatchObject({ status: 503, message: "Try again shortly." });
    expect(readAccessToken(storage)).toBe("access-1");
    expect(readRefreshToken(storage)).toBe("refresh-1");
  });

  it("keeps both tokens and rethrows when the refresh fails with a network error", async () => {
    const { storage, transport, apiClient } = setup();
    const networkError = new TypeError("Failed to fetch");
    transport.respondJson(401, { error: "Token expired." });
    transport.failNext(networkError);

    const error = await thrownBy(apiClient.requestAuthenticatedJson("/api/invitations/"));

    expect(error).toBe(networkError);
    expect(readAccessToken(storage)).toBe("access-1");
    expect(readRefreshToken(storage)).toBe("refresh-1");
  });

  it("keeps both tokens and rethrows when the retry fails with 500", async () => {
    const { storage, transport, apiClient } = setup();
    transport.respondJson(401, { error: "Token expired." });
    transport.respondJson(200, { access: "access-2" });
    transport.respondJson(500, { error: "Something went wrong." });

    const error = await thrownBy(apiClient.requestAuthenticatedJson("/api/invitations/"));

    expect(error).toMatchObject({ status: 500 });
    expect(readAccessToken(storage)).toBe("access-2");
    expect(readRefreshToken(storage)).toBe("refresh-1");
  });

  it("clears both tokens when the retry is 401 again", async () => {
    const { storage, transport, apiClient } = setup();
    transport.respondJson(401, { error: "Token expired." });
    transport.respondJson(200, { access: "access-2" });
    transport.respondJson(401, { error: "Token expired." });

    const error = await thrownBy(apiClient.requestAuthenticatedJson("/api/invitations/"));

    expect(error).toMatchObject({ status: 401 });
    expect(readAccessToken(storage)).toBeNull();
    expect(readRefreshToken(storage)).toBeNull();
    expect(transport.requests).toHaveLength(3);
  });

  it("clears the access token without a refresh request when there is no refresh token", async () => {
    const { storage, transport, apiClient } = setup(null);
    writeAccessToken(storage, "access-1");
    transport.respondJson(401, { error: "Token expired." });

    const error = await thrownBy(apiClient.requestAuthenticatedJson("/api/invitations/"));

    expect(error).toMatchObject({ status: 401 });
    expect(readAccessToken(storage)).toBeNull();
    expect(transport.requests).toHaveLength(1);
  });

  it("does not refresh and keeps both tokens when the first response is not 401", async () => {
    const { storage, transport, apiClient } = setup();
    transport.respondJson(404, { error: "Team team-9 was not found." });

    const error = await thrownBy(apiClient.requestAuthenticatedJson("/api/invitations/"));

    expect(error).toMatchObject({ status: 404, message: "Team team-9 was not found." });
    expect(transport.requests).toHaveLength(1);
    expect(readAccessToken(storage)).toBe("access-1");
    expect(readRefreshToken(storage)).toBe("refresh-1");
  });
});
