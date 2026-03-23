import { useParams } from 'react-router-dom';
import './IssueDetail.css';

export const IssueDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="issue-detail">
      <h1>이슈 상세</h1>
      <div className="issue-detail__id">
        <span>{id}</span>
      </div>
    </div>
  );
};
