import { NavLink } from 'react-router-dom';
import { NAV_ITEMS } from '../../constants/routes';
import './Sidebar.css';

export const Sidebar: React.FC = () => (
  <aside className="sidebar" role="complementary">
    <div className="sidebar__brand">
      <h1 className="sidebar__title">Personal Jira</h1>
    </div>
    <nav className="sidebar__nav">
      <ul className="sidebar__list">
        {NAV_ITEMS.map(({ path, label }) => (
          <li key={path} className="sidebar__item">
            <NavLink
              to={path}
              end={path === '/'}
              className={({ isActive }) =>
                `sidebar__link${isActive ? ' active' : ''}`
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
