import { useState } from 'react';
import type { Issue } from '@/types/issue';
import type { IssueStatus } from '@/types/issue';
import { useIssues } from '@/hooks/useIssues';
import { KanbanBoard } from '@/components/KanbanBoard';
import { CreateIssueDialog } from '@/components/CreateIssueDialog';
import { IssueDetailPanel } from '@/components/IssueDetailPanel';

export function App() {
  const { issues, createIssue, transitionIssue } = useIssues();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);

  const handleCreateIssue = async (title: string, description: string) => {
    await createIssue(title, description);
  };

  const handleStatusChange = async (id: string, status: IssueStatus) => {
    const updated = await transitionIssue(id, status);
    if (selectedIssue?.id === id) {
      setSelectedIssue(updated);
    }
  };

  return (
    <div>
      <header style={{ display: 'flex', justifyContent: 'space-between', padding: '1rem' }}>
        <h1>Personal Jira</h1>
        <button onClick={() => setDialogOpen(true)}>새 이슈</button>
      </header>
      <KanbanBoard issues={issues} onIssueClick={setSelectedIssue} />
      <CreateIssueDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onSubmit={handleCreateIssue}
      />
      {selectedIssue && (
        <IssueDetailPanel
          issue={selectedIssue}
          onClose={() => setSelectedIssue(null)}
          onStatusChange={handleStatusChange}
        />
      )}
    </div>
  );
}
