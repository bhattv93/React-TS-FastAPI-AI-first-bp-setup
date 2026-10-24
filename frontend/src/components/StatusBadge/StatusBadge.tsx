export type Status = 'ok' | 'error' | 'loading';

interface Props {
  status: Status;
  label: string;
}

const styles: Record<Status, string> = {
  ok: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
  loading: 'bg-gray-100 text-gray-700',
};

export function StatusBadge({ status, label }: Props) {
  return (
    <span
      role="status"
      className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${styles[status]}`}
    >
      {label}
    </span>
  );
}
