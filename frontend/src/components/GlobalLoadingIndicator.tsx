import { useIsFetching } from '@tanstack/react-query';

export function GlobalLoadingIndicator() {
  const isFetching = useIsFetching();

  if (isFetching === 0) {
    return null;
  }

  return (
    <div
      role="progressbar"
      aria-label="Loading"
      aria-valuenow={undefined}
      className="fixed inset-x-0 top-0 z-50 h-1 overflow-hidden bg-primary/20"
    >
      <div className="h-full w-1/3 animate-loading-bar bg-primary" />
    </div>
  );
}
