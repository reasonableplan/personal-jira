import { Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout";
import BoardPage from "@/pages/BoardPage";
import EpicsListPage from "@/pages/EpicsListPage";
import EpicDetailPage from "@/pages/EpicDetailPage";
import StoryDetailPage from "@/pages/StoryDetailPage";
import TaskDetailPage from "@/pages/TaskDetailPage";
import LabelsPage from "@/pages/LabelsPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/board" replace />} />
        <Route path="board" element={<BoardPage />} />
        <Route path="epics" element={<EpicsListPage />} />
        <Route path="epics/:id" element={<EpicDetailPage />} />
        <Route path="stories/:id" element={<StoryDetailPage />} />
        <Route path="tasks/:id" element={<TaskDetailPage />} />
        <Route path="settings/labels" element={<LabelsPage />} />
      </Route>
    </Routes>
  );
}
