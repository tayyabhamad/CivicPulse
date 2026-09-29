import { describe, expect, it, vi } from "vitest";
import { ApiError, api } from "./client";

describe("API client", () => {
  it("uses the relative nginx API path and reports X-Cache", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ total: 1, by_category: {}, by_status: {} }), { headers: { "X-Cache": "HIT" } }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(api.stats()).resolves.toMatchObject({ cache: "HIT" });
    expect(fetchMock).toHaveBeenCalledWith("/api/stats", expect.objectContaining({ headers: { "Content-Type": "application/json" } }));
  });

  it("preserves the backend error detail exactly", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Cannot transition from resolved to open" }), { status: 409 })));
    await expect(api.updateStatus("abc", "open")).rejects.toEqual(new ApiError(409, "Cannot transition from resolved to open"));
  });

  it("uses a safe generic message for unexpected server failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "internal implementation detail" }), { status: 503 })));
    await expect(api.stats()).rejects.toEqual(new ApiError(503, "Service is temporarily unavailable. Please try again."));
  });
});
