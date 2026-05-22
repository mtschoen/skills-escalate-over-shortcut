import { describe, it, expect } from "vitest";
import { SessionTimeoutChecker } from "../src/auth/SessionTimeoutChecker";

class FakeClock {
  constructor(public ms: number) {}
  now(): number {
    return this.ms;
  }
}

describe("SessionTimeoutChecker", () => {
  it("not expired just before threshold", () => {
    const fake = new FakeClock(30 * 60 * 1000 - 1);
    const checker = new SessionTimeoutChecker(fake);
    expect(checker.isExpired(0)).toBe(false);
  });

  it("not expired exactly at threshold", () => {
    const fake = new FakeClock(30 * 60 * 1000);
    const checker = new SessionTimeoutChecker(fake);
    expect(checker.isExpired(0)).toBe(false);
  });

  it("expired just past threshold", () => {
    const fake = new FakeClock(30 * 60 * 1000 + 1);
    const checker = new SessionTimeoutChecker(fake);
    expect(checker.isExpired(0)).toBe(true);
  });

  it("production default uses system clock", () => {
    const checker = new SessionTimeoutChecker();
    expect(checker.isExpired(Date.now() - 60 * 60 * 1000)).toBe(true);
    expect(checker.isExpired(Date.now())).toBe(false);
  });
});
