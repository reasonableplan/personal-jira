import { createBrowserRouter } from 'react-router-dom';

import { AppLayout } from '@/components/layout/AppLayout';
import { BoardPage } from '@/pages/BoardPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { EpicDetailPage } from '@/pages/EpicDetailPage';
import { EpicsPage } from '@/pages/EpicsPage';
import { LabelsPage } from '@/pages/LabelsPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'board', element: <BoardPage /> },
      { path: 'epics', element: <EpicsPage /> },
      { path: 'epics/:epicId', element: <EpicDetailPage /> },
      { path: 'labels', element: <LabelsPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);
