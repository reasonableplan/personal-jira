import { Outlet } from 'react-router-dom';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import './AppLayout.css';

export function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-layout-content">
        <Header />
        <main data-testid="app-main" className="app-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
