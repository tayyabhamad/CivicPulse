import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { ApiError, api } from "../api/client";
import { Dashboard } from "./Dashboard";

vi.mock("../api/client", async () => {
  const actual = await vi.importActual<typeof import("../api/client")>("../api/client");
  return { ...actual, api: { listComplaints: vi.fn(), stats: vi.fn(), updateStatus: vi.fn() } };
});

const item = { id: "complaint-1", text: "Flood", location: "Block A", reporter_contact: null, category: "water" as const, priority: "high" as const, status: "open" as const, ai_summary: "Road flooding", triaged_by: "rules", triage_latency_ms: 1 };
const stats = { data: { total: 1, by_category: { water: 1 }, by_status: { open: 1 } }, cache: "MISS" as const };

describe("Dashboard", () => {
  it("renders cache state and submits selected filters", async () => {
    vi.mocked(api.listComplaints).mockResolvedValue({ items: [item], total: 1 });
    vi.mocked(api.stats).mockResolvedValue(stats);
    const user = userEvent.setup(); render(<Dashboard refreshToken={0} />);
    expect(await screen.findByText("Stats cache: MISS")).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Filter category"), "water");
    expect(await screen.findByText("Road flooding")).toBeInTheDocument();
    expect(api.listComplaints).toHaveBeenLastCalledWith(expect.objectContaining({ category: "water", page: 1 }));
  });

  it("renders the server's 409 transition explanation verbatim", async () => {
    const resolvedItem = { ...item, status: "resolved" as const };
    vi.mocked(api.listComplaints).mockResolvedValue({ items: [resolvedItem], total: 1 });
    vi.mocked(api.stats).mockResolvedValue(stats);
    vi.mocked(api.updateStatus).mockRejectedValue(new ApiError(409, "Cannot transition from resolved to open"));
    const user = userEvent.setup(); render(<Dashboard refreshToken={0} />);
    await screen.findByText("Road flooding");
    const selector = screen.getByLabelText("Update complaint-1");
    expect(selector).toBeEnabled();
    await user.selectOptions(selector, "open");
    expect(await screen.findByRole("alert")).toHaveTextContent("Cannot transition from resolved to open");
  });

  it("shows loading, then retries a failed dashboard load", async () => {
    vi.mocked(api.listComplaints).mockRejectedValueOnce(new ApiError(503, "Service is temporarily unavailable. Please try again.")).mockResolvedValue({ items: [item], total: 1 });
    vi.mocked(api.stats).mockResolvedValue(stats);
    const user = userEvent.setup();
    render(<Dashboard refreshToken={0} />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading complaints");
    expect(await screen.findByRole("alert")).toHaveTextContent("Service is temporarily unavailable");
    const callsBeforeRetry = vi.mocked(api.listComplaints).mock.calls.length;
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findByText("Road flooding")).toBeInTheDocument();
    expect(api.listComplaints).toHaveBeenCalledTimes(callsBeforeRetry + 1);
  });

  it("disables only the complaint currently being updated", async () => {
    let finishUpdate: (() => void) | undefined;
    vi.mocked(api.listComplaints).mockResolvedValue({ items: [item], total: 1 });
    vi.mocked(api.stats).mockResolvedValue(stats);
    vi.mocked(api.updateStatus).mockReturnValue(new Promise<void>((resolve) => { finishUpdate = resolve; }) as never);
    const user = userEvent.setup(); render(<Dashboard refreshToken={0} />);
    const selector = await screen.findByLabelText("Update complaint-1");
    await user.selectOptions(selector, "in_progress");
    expect(selector).toBeDisabled();
    finishUpdate?.();
    await waitFor(() => expect(screen.getByLabelText("Update complaint-1")).toBeEnabled());
  });
});
