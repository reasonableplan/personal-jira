import { createBrowserRouter } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';

import { AppLayout } from '@/components/layout/AppLayout';
import {
  BoardPage,
  DashboardPage,
  EpicDetailPage,
  EpicsPage,
  LabelsPage,
  NotFoundPage,
} from '@/pages';

export const routeConfig: RouteObject[] = [
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
];

export const router = createBrowserRouter(routeConfig);
