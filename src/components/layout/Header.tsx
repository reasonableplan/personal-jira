import { useLocation, matchPath } from 'react-router-dom';
import { ROUTES, ROUTE_LABELS } from '../../constants/routes';
import type { RoutePath } from '../../constants/routes';
import './Header.css';

const ROUTE_PATTERNS: RoutePath[] = [
  ROUTES.DASHBOARD,
  ROUTES.BOARD,
  ROUTES.ISSUE_DETAIL,
];

const getPageTitle = (pathname: string): string => {
  for (const pattern of ROUTE_PATTERNS) {
    if (matchPath(pattern, pathname)) {
      return ROUTE_LABELS[pattern];
    }
  }
  return '';
};

export const Header: React.FC = () => {
  const { pathname } = useLocation();
  const title = getPageTitle(pathname);

  return (
    <header className="header">
      <h2 className="header__title">{title}</h2>
    </header>
  );
};
