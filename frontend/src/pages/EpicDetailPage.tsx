import { useParams } from 'react-router-dom';

export function EpicDetailPage() {
  const { epicId } = useParams<{ epicId: string }>();

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight">
        에픽 상세 #{epicId}
      </h1>
      <p className="mt-2 text-muted-foreground">에픽의 상세 정보입니다.</p>
    </div>
  );
}
