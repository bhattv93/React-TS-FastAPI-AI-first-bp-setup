interface Props {
  message: string;
}

/** Shown instead of the app when `/config.json` cannot be loaded. */
export function ConfigErrorScreen({ message }: Props) {
  return (
    <div role="alert" className="m-6 rounded border border-red-300 bg-red-50 p-4 text-red-800">
      <p className="font-semibold">The application could not start.</p>
      <p className="text-sm">{message}</p>
    </div>
  );
}
