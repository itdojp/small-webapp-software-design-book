import { describe, it, expect } from "vitest";
import { calcDueStatus } from "./calcDueStatus";

describe("calcDueStatus", () => {
  it("期限なしは ok", () => {
    expect(calcDueStatus(new Date("2026-01-01T00:00:00Z"))).toBe("ok");
  });
  it("期限超過は overdue", () => {
    expect(
      calcDueStatus(
        new Date("2026-01-02T00:00:00Z"),
        new Date("2026-01-01T00:00:00Z")
      )
    ).toBe("overdue");
  });
  it("期限まで2日は due_soon", () => {
    expect(
      calcDueStatus(
        new Date("2026-01-01T00:00:00Z"),
        new Date("2026-01-03T00:00:00Z")
      )
    ).toBe("due_soon");
  });
  it("期限まで2日より先は ok", () => {
    expect(
      calcDueStatus(
        new Date("2026-01-01T00:00:00Z"),
        new Date("2026-01-04T00:00:00Z")
      )
    ).toBe("ok");
  });
});
