import { describe, expect, it } from "vitest";
import { MemoryStorage } from "../testing/MemoryStorage";
import {
  clearAuthTokens,
  readAccessToken,
  readRefreshToken,
  writeAccessToken,
  writeAuthTokens,
} from "./AuthStorage";

describe("AuthStorage", () => {
  it("reads back both tokens it wrote and replaces only the access token on writeAccessToken", () => {
    const storage = new MemoryStorage();
    writeAuthTokens(storage, { access: "access-1", refresh: "refresh-1" });

    expect(readAccessToken(storage)).toBe("access-1");
    expect(readRefreshToken(storage)).toBe("refresh-1");

    writeAccessToken(storage, "access-2");

    expect(readAccessToken(storage)).toBe("access-2");
    expect(readRefreshToken(storage)).toBe("refresh-1");
  });

  it("clears both tokens and leaves unrelated keys alone", () => {
    const storage = new MemoryStorage();
    writeAuthTokens(storage, { access: "access-1", refresh: "refresh-1" });
    storage.setItem("theme", "dark");

    clearAuthTokens(storage);

    expect(readAccessToken(storage)).toBeNull();
    expect(readRefreshToken(storage)).toBeNull();
    expect(storage.getItem("theme")).toBe("dark");
  });
});
