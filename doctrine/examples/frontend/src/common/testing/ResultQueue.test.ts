import { describe, expect, it } from "vitest";
import { ResultQueue } from "./ResultQueue";

describe("ResultQueue", () => {
  it("returns queued results in order and throws on a call nobody queued a result for", async () => {
    const queue = new ResultQueue<string>("lookup");
    queue.resolveNext("first");
    queue.resolveNext("second");

    expect(await queue.next()).toBe("first");
    expect(await queue.next()).toBe("second");
    expect(() => queue.next()).toThrow("lookup was called more times than results were queued");
  });
});
