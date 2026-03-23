import { NavLink } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import './Sidebar.css';

const NAV_ITEMS = [
  { to: ROUTES.DASHBOARD, label: '대시보드' },
  { to: ROUTES.BOARD, label: '보드' },
] as const;

export function Sidebar() {
  return (
    <aside data-testid="app-sidebar" className="sidebar">
      <div className="sidebar-brand">
        <h1 className="sidebar-title">Personal Jira</h1>
      </div>
      <nav className="sidebar-nav">
        <ul className="sidebar-nav-list">
          {NAV_ITEMS.map(({ to, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={to === ROUTES.DASHBOARD}
                className={({ isActive }) =>
                  `sidebar-link${isActive ? ' active' : ''}`
                }
              >
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
