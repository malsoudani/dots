import { describe, expect, it } from "vitest";
import { Invitation } from "./Invitation";

describe("Invitation.fromResponse", () => {
  it("maps every wire field to its camelCase model field", () => {
    const invitation = Invitation.fromResponse({
      id: "inv-1",
      team_id: "team-1",
      email: "ana@example.com",
      role: "admin",
      status: "pending",
      message: "Welcome aboard",
      expires_at: "2030-01-31T23:59:59+00:00",
      created_at: "2030-01-01T09:00:00+00:00",
    });

    expect(invitation).toEqual({
      id: "inv-1",
      teamId: "team-1",
      email: "ana@example.com",
      role: "admin",
      status: "pending",
      message: "Welcome aboard",
      expiresAt: "2030-01-31T23:59:59+00:00",
      createdAt: "2030-01-01T09:00:00+00:00",
    });
  });

  it("defaults a missing or null message to empty and a missing or null expiry to null", () => {
    const required = {
      id: "inv-1",
      team_id: "team-1",
      email: "ana@example.com",
      role: "member",
      status: "revoked",
      created_at: "2030-01-01T09:00:00+00:00",
    } as const;

    const missing = Invitation.fromResponse(required);
    const explicitNull = Invitation.fromResponse({ ...required, message: null, expires_at: null });

    expect(missing).toMatchObject({ message: "", expiresAt: null });
    expect(explicitNull).toMatchObject({ message: "", expiresAt: null });
  });
});

describe("Invitation.isPending", () => {
  it("is true for a pending invitation and false for an accepted or revoked one", () => {
    const base = Invitation.fromResponse({
      id: "inv-1",
      team_id: "team-1",
      email: "ana@example.com",
      role: "member",
      status: "pending",
      created_at: "2030-01-01T09:00:00+00:00",
    });

    expect(Invitation.isPending(base)).toBe(true);
    expect(Invitation.isPending({ ...base, status: "accepted" })).toBe(false);
    expect(Invitation.isPending({ ...base, status: "revoked" })).toBe(false);
  });
});
