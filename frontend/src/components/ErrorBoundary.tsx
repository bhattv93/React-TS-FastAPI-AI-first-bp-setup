import { Component, type ErrorInfo, type ReactNode } from 'react';

import { getErrorMessage } from '../utils/errors';

interface Props {
  children: ReactNode;
}

interface State {
  error?: unknown;
}

/** Catches render errors below it and shows a fallback instead of a blank page. */
export class ErrorBoundary extends Component<Props, State> {
  override state: State = {};

  static getDerivedStateFromError(error: unknown): State {
    return { error };
  }

  override componentDidCatch(error: unknown, info: ErrorInfo): void {
    console.error('Render error', error, info.componentStack);
  }

  override render(): ReactNode {
    if (this.state.error !== undefined) {
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
