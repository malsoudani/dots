import { describe, expect, it } from "vitest";
import { TeamMember } from "./TeamMember";

describe("TeamMember.fromResponse", () => {
  it("maps id, email and name, and defaults a missing or null name to empty", () => {
    const wire = { id: "user-1", email: "ana@example.com" };

    expect(TeamMember.fromResponse({ ...wire, name: "Ana Example" })).toEqual({ ...wire, name: "Ana Example" });
    expect(TeamMember.fromResponse(wire)).toEqual({ ...wire, name: "" });
    expect(TeamMember.fromResponse({ ...wire, name: null })).toEqual({ ...wire, name: "" });
  });
});
