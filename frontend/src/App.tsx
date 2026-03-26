import { cn } from '@/lib/utils';

export function App() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1
          className={cn(
            'text-4xl font-bold tracking-tight text-foreground',
            'mb-4',
          )}
        >
          Personal Jira
        </h1>
        <p className="text-lg text-muted-foreground">
          프로젝트 관리 도구
        </p>
      </div>
    </div>
  );
}
