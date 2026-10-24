import { StatusBadge } from '../components/StatusBadge';
import { useHealth } from '../hooks/useHealth';
import { getErrorMessage } from '../utils/errors';

export function HomePage() {
  const health = useHealth();

  return (
    <main className="mx-auto max-w-xl p-6">
      <h1 className="text-2xl font-bold">AI-First App</h1>
      <p className="mt-2 text-gray-600">
        React + TypeScript frontend talking to a FastAPI backend.
      </p>
      <section aria-label="API status" className="mt-6 space-y-2">
        {health.isPending && <StatusBadge status="loading" label="Checking API..." />}
        {health.isError && (
          <div role="alert" className="text-red-700">
            <StatusBadge status="error" label="API unreachable" />
            <p className="mt-2 text-sm">{getErrorMessage(health.error)}</p>
          </div>
        )}
        {health.isSuccess && (
          <>
            <StatusBadge status="ok" label="API is healthy" />
            <p className="text-sm text-gray-600">
              Version {health.data.version} ({health.data.env})
            </p>
          </>
        )}
      </section>
    </main>
  );
}
