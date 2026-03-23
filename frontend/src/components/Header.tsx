import { useLocation } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import './Header.css';

const PAGE_TITLES: Record<string, string> = {
  [ROUTES.DASHBOARD]: '대시보드',
  [ROUTES.BOARD]: '보드',
};

export function Header() {
  const { pathname } = useLocation();

  const title = PAGE_TITLES[pathname] ?? (pathname.startsWith('/issues/') ? '이슈 상세' : '');

  return (
    <header data-testid="app-header" className="header">
      <div data-testid="header-title" className="header-title">
        {title}
      </div>
    </header>
  );
}
