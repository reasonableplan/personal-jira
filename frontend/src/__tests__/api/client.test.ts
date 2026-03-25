import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { apiClient, ApiRequestError } from "@/api/client";

const BASE_URL = "/api";

describe("apiClient", () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", mockFetch);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("GET request prepends base URL", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ items: [], total: 0 }),
    });
    await apiClient.get("/epics");
    expect(mockFetch).toHaveBeenCalledWith(`${BASE_URL}/epics`, expect.objectContaining({ method: "GET" }));
  });

  it("POST sends JSON body", async () => {
    const body = { title: "New Epic" };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: () => Promise.resolve({ id: "1", ...body }),
    });
    await apiClient.post("/epics", body);
    expect(mockFetch).toHaveBeenCalledWith(
      `${BASE_URL}/epics`,
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify(body),
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
      }),
    );
  });

  it("PATCH sends JSON body", async () => {
    const body = { title: "Updated" };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ id: "1", ...body }),
    });
    await apiClient.patch("/epics/1", body);
    expect(mockFetch).toHaveBeenCalledWith(
      `${BASE_URL}/epics/1`,
      expect.objectContaining({ method: "PATCH", body: JSON.stringify(body) }),
    );
  });

  it("DELETE returns void on 204", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, status: 204 });
    const result = await apiClient.delete("/epics/1");
    expect(result).toBeUndefined();
  });

  it("throws ApiRequestError on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: "Not found" }),
    });
    await expect(apiClient.get("/epics/999")).rejects.toThrow(ApiRequestError);
  });

  it("ApiRequestError contains status and detail", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 409,
      json: () => Promise.resolve({ detail: "Conflict" }),
    });
    try {
      await apiClient.post("/tasks/1/claim", { agent_id: "a1" });
      expect.unreachable("should have thrown");
    } catch (e) {
      expect(e).toBeInstanceOf(ApiRequestError);
      const err = e as ApiRequestError;
      expect(err.status).toBe(409);
      expect(err.detail).toBe("Conflict");
    }
  });

  it("handles non-JSON error response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.reject(new Error("not json")),
    });
    await expect(apiClient.get("/epics")).rejects.toThrow(ApiRequestError);
  });

  it("GET with query params appends to URL", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ items: [], total: 0 }),
    });
    await apiClient.get("/tasks?status=backlog&page=1");
    expect(mockFetch).toHaveBeenCalledWith(`${BASE_URL}/tasks?status=backlog&page=1`, expect.any(Object));
  });
});
