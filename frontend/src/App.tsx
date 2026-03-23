import { KanbanBoard } from '@/components/KanbanBoard';
import styles from './App.module.css';

export default function App() {
  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <h1 className={styles.title}>Personal JIRA</h1>
      </header>
      <main>
        <KanbanBoard />
      </main>
    </div>
  );
}
