import { describe, expect, it } from "vitest";
import { expirySummary, pendingSummary, submitLabel } from "./invitationsCopy";

describe("invitationsCopy", () => {
  it("words each submit intent, the pending count and the expiry", () => {
    expect(submitLabel("invite")).toBe("Send invitation");
    expect(submitLabel("invite-with-expiry")).toBe("Send invitation with expiry");
    expect(pendingSummary(0)).toBe("No pending invitations");
    expect(pendingSummary(1)).toBe("1 pending invitation");
    expect(pendingSummary(3)).toBe("3 pending invitations");
    expect(expirySummary(null)).toBe("No expiry");
    expect(expirySummary("2030-01-31T23:59:59+00:00")).toBe("Expires 2030-01-31");
  });
});
