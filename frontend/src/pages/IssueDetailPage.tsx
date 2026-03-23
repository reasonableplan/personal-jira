import { useParams } from 'react-router-dom';

export function IssueDetailPage() {
  const { id } = useParams<{ id: string }>();

  return (
    <div data-testid="issue-detail-page">
      <h2>이슈 상세</h2>
      <p>이슈 ID: {id}</p>
    </div>
  );
}
