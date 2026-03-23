import { Link } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';

export function NotFoundPage() {
  return (
    <div data-testid="not-found-page">
      <h2>404</h2>
      <p>페이지를 찾을 수 없습니다.</p>
      <Link to={ROUTES.DASHBOARD}>대시보드로 돌아가기</Link>
    </div>
  );
}
