import { describe, expect, it } from "vitest";
import { isExpiryEnabled } from "./InvitationFlags";

describe("isExpiryEnabled", () => {
  it("is true for true, 1 and yes in any case and with surrounding spaces", () => {
    for (const value of ["true", "1", "yes", " TRUE ", "Yes"]) {
      expect(isExpiryEnabled({ VITE_INVITATION_EXPIRY: value }), value).toBe(true);
    }
  });

  it("is false for false, 0 and no, and defaults to false when unset or unrecognized", () => {
    for (const value of ["false", "0", "no", "No", "", "maybe"]) {
      expect(isExpiryEnabled({ VITE_INVITATION_EXPIRY: value }), value).toBe(false);
    }
    expect(isExpiryEnabled({})).toBe(false);
  });
});
