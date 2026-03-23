import { DarkModeToggle } from './components/DarkModeToggle';

export function App() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors">
      <header className="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-gray-700">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Personal Jira</h1>
        <DarkModeToggle />
      </header>
    </div>
  );
}
