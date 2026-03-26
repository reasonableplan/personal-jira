interface ErrorFallbackProps {
  error: Error;
  onReset: () => void;
}

export function ErrorFallback({ error, onReset }: ErrorFallbackProps) {
  return (
    <div
      role="alert"
      className="flex min-h-screen flex-col items-center justify-center gap-4 p-8"
    >
      <div className="text-center">
        <h1 className="mb-2 text-2xl font-bold text-foreground">
          문제가 발생했습니다
        </h1>
        <p className="mb-4 max-w-md text-sm text-muted-foreground">
          예기치 않은 오류가 발생했습니다. 아래 버튼을 클릭하여 다시 시도해
          주세요.
        </p>
        <pre className="mb-4 max-w-lg overflow-auto rounded-md bg-muted p-4 text-left text-xs text-muted-foreground">
          {error.message}
        </pre>
      </div>
      <button
        type="button"
        onClick={onReset}
        className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
      >
        다시 시도
      </button>
    </div>
  );
}
