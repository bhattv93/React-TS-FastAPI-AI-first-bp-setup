import { Component, type ErrorInfo, type ReactNode } from 'react';

import { getErrorMessage } from '../utils/errors';

interface Props {
  children: ReactNode;
  /** When this value changes, a displayed error is cleared (for example on navigation). */
  resetKey?: unknown;
}

interface State {
  hasError: boolean;
  error?: unknown;
}

/** Catches render errors below it and shows a fallback instead of a blank page. */
export class ErrorBoundary extends Component<Props, State> {
  override state: State = { hasError: false };

  static getDerivedStateFromError(error: unknown): State {
    return { hasError: true, error };
  }

  override componentDidCatch(error: unknown, info: ErrorInfo): void {
    console.error('Render error', error, info.componentStack);
  }

  override componentDidUpdate(previous: Props): void {
    if (this.state.hasError && previous.resetKey !== this.props.resetKey) {
      this.setState({ hasError: false, error: undefined });
    }
  }

  override render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div role="alert" className="m-6 rounded border border-red-300 bg-red-50 p-4 text-red-800">
          <p className="font-semibold">Something went wrong.</p>
          <p className="text-sm">{getErrorMessage(this.state.error)}</p>
        </div>
      );
    }
    return this.props.children;
  }
}
