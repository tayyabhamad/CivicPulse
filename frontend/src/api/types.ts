export const categories = [
  "water",
  "electricity",
  "sanitation",
  "roads",
  "streetlights",
  "other"
] as const;
export const priorities = ["high", "normal", "low"] as const;
export const complaintStatuses = ["open", "in_progress", "resolved", "rejected"] as const;

export type Category = components["schemas"]["Category"];
export type Priority = components["schemas"]["Priority"];
export type ComplaintStatus = components["schemas"]["ComplaintStatus"];

export type ComplaintCreate = components["schemas"]["ComplaintCreate"];
export type Complaint = components["schemas"]["ComplaintRead"];
export type ComplaintPage = components["schemas"]["ComplaintListRead"];
export type Stats = components["schemas"]["ComplaintStatsRead"];

export interface StatsResponse {
  data: Stats;
  cache: "HIT" | "MISS" | "UNKNOWN";
}

export interface ComplaintFilters {
  category?: Category;
  priority?: Priority;
  status?: ComplaintStatus;
  page: number;
  pageSize: number;
}
import type { components } from "./openapi.generated";
