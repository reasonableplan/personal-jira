import { QueryClientProvider } from '@tanstack/react-query';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { App } from '@/App';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { GlobalLoadingIndicator } from '@/components/GlobalLoadingIndicator';
import { Toaster } from '@/components/ui/sonner';
import '@/index.css';
import { queryClient } from '@/lib/query-client';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Root element not found');
}

createRoot(rootElement).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <GlobalLoadingIndicator />
        <App />
        <Toaster position="top-right" richColors closeButton />
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>,
);
