import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { ApiError, api } from "../api/client";
import { ComplaintForm } from "./ComplaintForm";

vi.mock("../api/client", async () => {
  const actual = await vi.importActual<typeof import("../api/client")>("../api/client");
  return { ...actual, api: { createComplaint: vi.fn() } };
});

describe("ComplaintForm", () => {
  it("mirrors the server minimum text validation before sending", async () => {
    const user = userEvent.setup();
    render(<ComplaintForm onCreated={vi.fn()} />);
    await user.type(screen.getByLabelText("What happened?"), "too short");
    await user.type(screen.getByLabelText("Location"), "Mall");
    await user.click(screen.getByRole("button", { name: "Submit complaint" }));
    expect(screen.getByRole("alert")).toHaveTextContent("at least 10 characters");
    expect(api.createComplaint).not.toHaveBeenCalled();
  });

  it("shows an honest loading state and returned triage details", async () => {
    const user = userEvent.setup();
    let resolveRequest: ((value: never) => void) | undefined;
    vi.mocked(api.createComplaint).mockReturnValue(new Promise((resolve) => { resolveRequest = resolve as (value: never) => void; }));
    render(<ComplaintForm onCreated={vi.fn()} />);
    await user.type(screen.getByLabelText("What happened?"), "Water is flooding the street outside school");
    await user.type(screen.getByLabelText("Location"), "Model Town");
    await user.click(screen.getByRole("button", { name: "Submit complaint" }));
    expect(screen.getByRole("button", { name: "Submitting…" })).toBeDisabled();
    resolveRequest?.({ id: "1", text: "x", location: "Model Town", reporter_contact: null, category: "water", priority: "high", status: "open", ai_summary: "Flooding near school", triaged_by: "rules", triage_latency_ms: 3 } as never);
    expect(await screen.findByText("Complaint received")).toBeInTheDocument();
    expect(screen.getByText("Triage provider: rules (3 ms)")).toBeInTheDocument();
  });

  it("shows a server rate-limit explanation and lets the resident retry", async () => {
    const user = userEvent.setup();
    vi.mocked(api.createComplaint).mockRejectedValue(new ApiError(429, "Too many submissions. Please wait before trying again."));
    render(<ComplaintForm onCreated={vi.fn()} />);
    await user.type(screen.getByLabelText("What happened?"), "Water is flooding the street outside school");
    await user.type(screen.getByLabelText("Location"), "Model Town");
    await user.click(screen.getByRole("button", { name: "Submit complaint" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Too many submissions. Please wait before trying again.");
    expect(screen.getByRole("button", { name: "Submit complaint" })).toBeEnabled();
  });
});
