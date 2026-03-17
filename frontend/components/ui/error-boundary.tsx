"use client";

import { Component, ReactNode, ErrorInfo } from "react";
import { useRouter } from "next/navigation";
import { Button } from "./button";

interface Props {
  children: ReactNode;
  fallback?: (error: Error, retry: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundaryComponent extends Component<Props, State> {
  public constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      return this.props.fallback ? (
        this.props.fallback(this.state.error!, this.handleRetry)
      ) : (
        <DefaultErrorFallback error={this.state.error!} onRetry={this.handleRetry} />
      );
    }

    return this.props.children;
  }
}

interface DefaultErrorFallbackProps {
  error: Error;
  onRetry: () => void;
}

function DefaultErrorFallback({ error, onRetry }: DefaultErrorFallbackProps) {
  const router = useRouter();

  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="max-w-md text-center">
        <div className="text-5xl mb-4">⚠️</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h2>
        <p className="text-gray-600 mb-4">
          {error.message || "An unexpected error occurred"}
        </p>
        {process.env.NODE_ENV === "development" && (
          <details className="mb-6 p-4 bg-gray-100 rounded-lg text-left">
            <summary className="cursor-pointer font-mono text-sm text-gray-700">
              Error details
            </summary>
            <pre className="mt-2 text-xs overflow-auto max-h-48 text-gray-600">
              {error.stack}
            </pre>
          </details>
        )}
        <div className="flex gap-3 justify-center">
          <Button variant="primary" onClick={onRetry}>
            Try Again
          </Button>
          <Button
            variant="secondary"
            onClick={() => router.push("/")}
          >
            Go Home
          </Button>
        </div>
      </div>
    </div>
  );
}

export function ErrorBoundary(props: Props) {
  return <ErrorBoundaryComponent {...props} />;
}
