import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './pages/Dashboard';
import { Board } from './pages/Board';
import { IssueDetail } from './pages/IssueDetail';
import { NotFound } from './pages/NotFound';
import { ROUTES } from './constants/routes';
import './App.css';

export const App: React.FC = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<AppLayout />}>
        <Route path={ROUTES.DASHBOARD} element={<Dashboard />} />
        <Route path={ROUTES.BOARD} element={<Board />} />
        <Route path={ROUTES.ISSUE_DETAIL} element={<IssueDetail />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  </BrowserRouter>
);
