import type {
  Complaint,
  ComplaintCreate,
  ComplaintFilters,
  ComplaintPage,
  ComplaintStatus,
  StatsResponse
} from "./types";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const safeServerError = "Service is temporarily unavailable. Please try again.";

async function errorFrom(response: Response): Promise<ApiError> {
  if (response.status >= 500) return new ApiError(response.status, safeServerError);
  const body: unknown = await response.json().catch(() => null);
  const detail =
    typeof body === "object" && body !== null && "detail" in body && typeof body.detail === "string"
      ? body.detail
      : `Request failed (${response.status})`;
  return new ApiError(response.status, detail);
}

async function requestResponse(path: string, options?: RequestInit): Promise<Response> {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers }
  });
  if (!response.ok) throw await errorFrom(response);
  return response;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await requestResponse(path, options);
  return (await response.json()) as T;
}

export const api = {
  createComplaint(payload: ComplaintCreate): Promise<Complaint> {
    return request<Complaint>("/complaints", { method: "POST", body: JSON.stringify(payload) });
  },

  listComplaints(filters: ComplaintFilters): Promise<ComplaintPage> {
    const params = new URLSearchParams({ page: String(filters.page), page_size: String(filters.pageSize) });
    if (filters.category) params.set("category", filters.category);
    if (filters.priority) params.set("priority", filters.priority);
    if (filters.status) params.set("status", filters.status);
    return request<ComplaintPage>(`/complaints?${params.toString()}`);
  },

  updateStatus(id: string, status: ComplaintStatus): Promise<Complaint> {
    return request<Complaint>(`/complaints/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    });
  },

  async stats(): Promise<StatsResponse> {
    const response = await requestResponse("/stats");
    const cacheHeader = response.headers.get("X-Cache");
    return {
      data: (await response.json()) as StatsResponse["data"],
      cache: cacheHeader === "HIT" || cacheHeader === "MISS" ? cacheHeader : "UNKNOWN"
    };
  }
};
