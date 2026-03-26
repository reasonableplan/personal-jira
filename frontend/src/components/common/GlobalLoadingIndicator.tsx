import { useIsFetching } from '@tanstack/react-query';

export function GlobalLoadingIndicator() {
  const isFetching = useIsFetching();

  if (!isFetching) {
    return null;
  }

  return (
    <div
      role="progressbar"
      aria-label="데이터 로딩 중"
      className="fixed left-0 top-0 z-50 h-1 w-full overflow-hidden bg-primary/20"
    >
      <div className="h-full w-1/3 animate-[loading_1.5s_ease-in-out_infinite] bg-primary" />
    </div>
  );
}
