import { describe, it, expect } from "vitest";
import { hashToken } from "../src/auth/authenticate";

describe("hashToken", () => {
  it("hashes the empty string", () => {
    expect(hashToken("")).toBe(
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    );
  });

  it("hashes a basic ASCII string", () => {
    expect(hashToken("hello")).toBe(
      "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
    );
  });

  it("hashes a long Unicode string", () => {
    const s = "héllo wörld " + "🚀".repeat(100);
    expect(typeof hashToken(s)).toBe("string");
    expect(hashToken(s)).toHaveLength(64);
  });
});
