export function LoadingCard({ lines = 3 }) {
  return (
    <div className="card animate-pulse space-y-3">
      {Array.from({ length: lines }).map((_, index) => (
        <div key={index} className="h-4 rounded bg-slate-200 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export function ErrorMessage({ message }) {
  if (!message) return null;
  return <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950">{message}</div>;
}
