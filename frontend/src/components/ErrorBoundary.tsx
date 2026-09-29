import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props { children: ReactNode }
interface State { hasError: boolean }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State { return { hasError: true }; }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("CivicPulse UI error", error, info);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return <main className="fatal-error"><h1>Something went wrong</h1><p>Refresh the page to restore CivicPulse.</p></main>;
    }
    return this.props.children;
  }
}
