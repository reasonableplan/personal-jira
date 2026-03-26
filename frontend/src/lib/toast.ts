import { toast } from 'sonner';

import type { AppError } from '@/api/client';

export function showApiError(error: AppError): void {
  const detail =
    typeof error.detail === 'string' ? error.detail : error.message;

  toast.error('요청 실패', {
    description: detail,
  });
}
