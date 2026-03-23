import { Link } from 'react-router-dom';
import { ROUTES } from '../constants/routes';
import './NotFound.css';

export const NotFound: React.FC = () => (
  <div className="not-found">
    <h1 className="not-found__code">404</h1>
    <p className="not-found__message">페이지를 찾을 수 없습니다</p>
    <Link to={ROUTES.DASHBOARD} className="not-found__link">
      대시보드로 돌아가기
    </Link>
  </div>
);
