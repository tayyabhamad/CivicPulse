import { render, screen } from "@testing-library/react";
import { ErrorBoundary } from "./ErrorBoundary";

function BrokenChild(): never {
  throw new Error("broken test component");
}

describe("ErrorBoundary", () => {
  it("shows a recovery message when a child render fails", () => {
    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => undefined);
    render(<ErrorBoundary><BrokenChild /></ErrorBoundary>);
    expect(screen.getByRole("heading", { name: "Something went wrong" })).toBeInTheDocument();
    expect(screen.getByText("Refresh the page to restore CivicPulse.")).toBeInTheDocument();
    errorSpy.mockRestore();
  });
});
