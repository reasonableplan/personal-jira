import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import './AppLayout.css';

export const AppLayout: React.FC = () => (
  <div className="app-layout">
    <Sidebar />
    <div className="app-layout__content">
      <Header />
      <main className="app-layout__main">
        <Outlet />
      </main>
    </div>
  </div>
);
